import json
import requests
import re
from config import LLM_API_KEY, LLM_API_BASE, LLM_CHAT_MODEL
from prompts.review_prompt import REVIEW_PROMPT

def review_code(code, language):
    if not LLM_API_KEY:
        return {
            'summary': {'total_lines': len(code.splitlines()), 'issues_count': 0},
            'issues': [],
            'full_fixed_code': code,
            'error': '未配置 LLM_API_KEY'
        }

    prompt = REVIEW_PROMPT.format(language=language, code=code)

    try:
        resp = requests.post(
            f'{LLM_API_BASE}/chat/completions',
            headers={
                'Authorization': f'Bearer {LLM_API_KEY}',
                'Content-Type': 'application/json'
            },
            json={
                'model': LLM_CHAT_MODEL,
                'messages': [{'role': 'user', 'content': prompt}],
                'temperature': 0.3,
                'max_tokens': 4096
            },
            timeout=60
        )
        resp.raise_for_status()
        data = resp.json()
        content = data['choices'][0]['message']['content']
        return parse_review_result(content, code)
    except Exception as e:
        return {
            'summary': {'total_lines': len(code.splitlines()), 'issues_count': 0},
            'issues': [],
            'full_fixed_code': code,
            'error': str(e)
        }

def _norm(s):
    """归一化：去掉所有空白和引号。
    AI 常对 original_code 做"清洗"（随意增减空格、补/删引号），
    例如源码是 printf(Hello Word") 而片段写成 printf(Hello Word)，
    直接比较或包含都会失败，归一化后才能对上。"""
    return re.sub(r'[\s"\'`]+', '', str(s))


def _line_match(src_stripped, target_stripped):
    """单行匹配，从严到宽三级：
    1) 完全相等；2) 互相包含；3) 归一化(去空白/引号)后相等或包含。
    任一侧为空都算不匹配——空串做包含判断会恒为真（'' in 任意字符串 == True），必须挡掉。"""
    if not src_stripped or not target_stripped:
        return False
    if src_stripped == target_stripped:
        return True
    if target_stripped in src_stripped or src_stripped in target_stripped:
        return True
    ns, nt = _norm(src_stripped), _norm(target_stripped)
    if not ns or not nt:
        return False
    return ns == nt or nt in ns or ns in nt


# 会导致编译/解析失败的语法类问题关键词，命中即强制升级为 error（AI 偶尔会把缺分号等错判成 warning）
_SYNTAX_ERROR_KEYWORDS = (
    '缺少分号', '缺失分号', '少分号', '缺少引号', '未加引号', '字符串未加引号',
    '未声明', '未定义', '括号不匹配', '缺少括号', '缺少右括号', '缺少右花括号',
    '语法错误', '未闭合', '未结束',
)


def _should_be_error(issue):
    text = f"{issue.get('title', '')}{issue.get('description', '')}{issue.get('category', '')}"
    return any(k in text for k in _SYNTAX_ERROR_KEYWORDS)


def _changed_indices(orig_snippet, fixed_snippet):
    """对比"原片段"与"修改后片段"的非空行，返回原片段中被改动行的索引集合。
    只有两者非空行数一致才能逐行对齐；行数不一致(AI 增删行)返回 None 表示无法判断。
    比较时忽略纯空白/缩进差异——上下文行(如单独的 })只是缩进被 AI 调整不算"被修复"；
    但分号、引号等标点变化仍算改动(那才是真正的问题行)。"""
    if not fixed_snippet:
        return None
    o = [l.strip() for l in str(orig_snippet).splitlines() if l.strip()]
    f = [l.strip() for l in str(fixed_snippet).splitlines() if l.strip()]
    if len(o) != len(f) or not o:
        return None
    ws = lambda s: re.sub(r'\s+', '', s)  # 只去空白，保留标点
    changed = [i for i in range(len(o)) if ws(o[i]) != ws(f[i])]
    return changed or None


def _is_context_only(text):
    """判断一行是否只是括号/分号等结构性符号(如单独的 }、{、});)——这类是上下文，不是问题行。"""
    return re.sub(r'[\s{}();,\[\]]+', '', str(text)) == ''


def _find_candidate_lines(snippet, source_lines, fixed_snippet=None):
    """用问题片段(original_code)在源码中找问题所在行号(1-based)。
    - 多行片段：在"非空行序列"上按连续代码块匹配；若能拿到 fixed_code，
      只保留"原代码 vs 修改后代码"发生变化的行（上下文未改动行不算问题行）；
    - 单行片段：收集所有匹配行（处理两行代码完全相同的情况）。
    空行/纯空格不参与匹配；片段为空（空行类问题）返回空列表。"""
    if not snippet:
        return []
    snip = [l.strip() for l in str(snippet).splitlines() if l.strip()]
    if not snip:
        return []
    # 源码的非空行，保留原始行号（1-based），空行一律不参与匹配
    src_nonempty = [(i, l.strip()) for i, l in enumerate(source_lines, start=1) if l.strip()]
    n = len(snip)
    # 多行：在非空行序列上滑动找连续匹配块
    if n >= 2:
        for start in range(len(src_nonempty) - n + 1):
            window = src_nonempty[start:start + n]  # 与 snip 逐行对齐，元素为(真实行号, 文本)
            if all(_line_match(wl, sl) for (_, wl), sl in zip(window, snip)):
                # 1) 优先用 fixed_code 找出块内真正被改动的行，避免把上下文行(如 }) 当成问题行
                changed = _changed_indices(snippet, fixed_snippet)
                if changed:
                    cands = [window[i][0] for i in changed if i < len(window)]
                    if cands:
                        return cands
                # 2) 无法对齐(AI 增删行)时：排除纯括号/分号的上下文行(单独的 } { });)，锁定真正有代码的行
                code_like = [lineno for lineno, txt in window if not _is_context_only(txt)]
                if code_like:
                    return code_like
                return [lineno for lineno, _ in window]
    # 单行（或多行块未命中）：取最长行，先收集精确匹配，再退化包含匹配
    target = max(snip, key=len)
    exact = [i for i, l in src_nonempty if l == target]
    if exact:
        return exact
    return [i for i, l in src_nonempty if _line_match(l, target)]


def _pick_line(cands, ai_line, used_lines):
    """从候选行里选最可信的一行。
    排序键 (是否已占用, 离AI行号距离, 行号)：
    - 「占用优先」是刻意的——当两行代码完全相同(如重复的 printf)时，多个问题的候选行一样，
      必须让后来的问题避开已占行、落到另一行，否则两个问题会挤到同一行；
    - 「距离」只是同一行有多个可选位置时的次要参考。
    注意：不要改成 (距离, 占用)，否则重复代码行会重新撞车。
    同一行本就该有多个问题时不受影响——那种情况该 issue 只有一个匹配候选，占用与否都会选它。"""
    if not cands:
        return None
    def sort_key(ln):
        used = 1 if ln in used_lines else 0
        dist = abs(ln - ai_line) if isinstance(ai_line, (int, float)) else 0
        return (used, dist, ln)
    return sorted(cands, key=sort_key)[0]


def parse_review_result(content, original_code):
    try:
        json_match = re.search(r'\{[\s\S]*\}', content)
        if json_match:
            result = json.loads(json_match.group())
            # 行数、问题数是客观事实，一律以程序精确计算为准，不采信 AI（AI 数行数容易漏数空行/末行）
            if not isinstance(result.get('summary'), dict):
                result['summary'] = {}
            source_lines = original_code.splitlines()
            result['summary']['total_lines'] = len(source_lines)
            # 行号校准：用 AI 返回的 original_code 片段去源码里定位真实行，覆盖 AI 偏差的 line
            # 结合 AI 行号就近选择，并避免多个问题挤到同一行（处理重复代码行）
            issues = result.get('issues')
            if isinstance(issues, list):
                used_lines = set()
                for issue in issues:
                    if not isinstance(issue, dict):
                        continue
                    cands = _find_candidate_lines(
                        issue.get('original_code'), source_lines, issue.get('fixed_code'))
                    real_line = _pick_line(cands, issue.get('line'), used_lines)
                    if real_line:
                        issue['line'] = real_line
                        used_lines.add(real_line)
                    # 严重程度校准：缺分号/缺引号/未声明变量等语法错误强制算 error
                    if issue.get('severity') != 'error' and _should_be_error(issue):
                        issue['severity'] = 'error'
                result['issues'] = issues
            result['summary']['issues_count'] = len(result.get('issues', []))
            return result
    except json.JSONDecodeError:
        pass

    return {
        'summary': {'total_lines': len(original_code.splitlines()), 'issues_count': 0},
        'issues': [],
        'full_fixed_code': original_code,
        'raw_response': content
    }

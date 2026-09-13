import re

LANGUAGE_PATTERNS = {
    'python': [r'import\s+', r'def\s+', r'print\s*\(', r'#.*', r"'''", r'"""'],
    'javascript': [r'function\s+', r'const\s+', r'let\s+', r'var\s+', r'=>', r'console\.log'],
    'typescript': [r'import\s+.*from', r'interface\s+', r':\s*(string|number|boolean)', r'type\s+'],
    'java': [r'public\s+class', r'System\.out\.print', r'package\s+', r'@Override'],
    'cpp': [r'#include\s*[<"]', r'std::', r'int\s+main\s*\(', r'using\s+namespace'],
    'c': [r'#include\s*[<"]', r'int\s+main\s*\(', r'stdio\.h'],
    'html': [r'<html', r'<head', r'<body', r'<div'],
    'css': [r'\{[^}]*\}', r'@media', r'\.[a-z]+', r'#[a-z]+'],
    'vue': [r'<template', r'<script', r'export\s+default', r'v-bind', r'v-model'],
    'go': [r'package\s+main', r'func\s+', r'fmt\.Print'],
    'rust': [r'fn\s+', r'let\s+mut', r'use\s+std', r'impl\s+'],
    'sql': [r'SELECT\s+', r'INSERT\s+INTO', r'CREATE\s+TABLE', r'FROM\s+'],
    'json': [r'^\s*\{', r'^\s*\[.*\]'],
    'yaml': [r'^\s*[a-z-]+\s*:', r'^\s*-?\s*[a-z-]+\s*:'],
}

def detect_language(code):
    if not code or not code.strip():
        return 'plaintext', 0.0

    scores = {}
    for lang, patterns in LANGUAGE_PATTERNS.items():
        score = 0
        for pattern in patterns:
            if re.search(pattern, code, re.IGNORECASE | re.MULTILINE):
                score += 1
        scores[lang] = score / len(patterns)

    best_lang = max(scores, key=scores.get)
    confidence = scores[best_lang]

    if confidence < 0.2:
        return 'plaintext', confidence

    return best_lang, round(confidence, 2)

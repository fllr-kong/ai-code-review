<template>
  <div class="editor-panel">
    <div class="toolbar">
      <div class="toolbar-left">
        <div class="toolbar-label">
          <el-icon :size="16" color="var(--brand-primary)"><EditPen /></el-icon>
          <span>代码编辑器</span>
        </div>
        <el-select
          :modelValue="language"
          placeholder="选择语言"
          style="width: 140px"
          @update:modelValue="onLanguageUpdate"
          @change="onLanguageChange"
        >
          <el-option label="自动检测" value="" />
          <el-option label="Python" value="python" />
          <el-option label="JavaScript" value="javascript" />
          <el-option label="TypeScript" value="typescript" />
          <el-option label="Java" value="java" />
          <el-option label="C++" value="cpp" />
          <el-option label="C" value="c" />
          <el-option label="HTML" value="html" />
          <el-option label="CSS" value="css" />
          <el-option label="Vue" value="vue" />
          <el-option label="Go" value="go" />
          <el-option label="Rust" value="rust" />
          <el-option label="SQL" value="sql" />
          <el-option label="JSON" value="json" />
          <el-option label="YAML" value="yaml" />
        </el-select>
        <el-button :icon="Upload" @click="triggerUpload" round>上传文件</el-button>
        <input ref="fileInput" type="file" accept=".py,.js,.ts,.java,.cpp,.c,.html,.css,.vue,.go,.rs,.sql,.json,.yaml,.txt" hidden @change="onFileChange" />
      </div>
      <div class="toolbar-right">
        <el-button type="primary" :icon="VideoPlay" :loading="loading" @click="$emit('submit')" size="large" round>
          {{ loading ? '审查中...' : '提交审查' }}
        </el-button>
      </div>
    </div>
    <div ref="editorRef" class="editor-container"></div>
    <transition name="fade">
      <div v-if="detecting" class="detecting-tip">
        <el-icon class="spin"><Loading /></el-icon>
        正在检测语言...
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import * as monaco from 'monaco-editor'
import { Upload, VideoPlay, EditPen, Loading } from '@element-plus/icons-vue'
import { detectLanguage } from '../api'

const props = defineProps({
  modelValue: { type: String, default: '' },
  language: { type: String, default: '' },
  loading: { type: Boolean, default: false }
})

const emit = defineEmits(['update:modelValue', 'update:language', 'submit'])

const editorRef = ref(null)
const fileInput = ref(null)
const detecting = ref(false)
let editor = null

const languageMap = {
  python: 'python',
  javascript: 'javascript',
  typescript: 'typescript',
  java: 'java',
  cpp: 'cpp',
  c: 'c',
  html: 'html',
  css: 'css',
  vue: 'html',
  go: 'go',
  rust: 'rust',
  sql: 'sql',
  json: 'json',
  yaml: 'yaml'
}

onMounted(() => {
  editor = monaco.editor.create(editorRef.value, {
    value: props.modelValue,
    language: languageMap[props.language] || 'plaintext',
    theme: 'vs-dark',
    fontSize: 14,
    fontFamily: "'Fira Code', 'Consolas', 'Monaco', monospace",
    minimap: { enabled: false },
    scrollBeyondLastLine: false,
    automaticLayout: true,
    tabSize: 4,
    wordWrap: 'on',
    padding: { top: 12 },
    lineNumbers: 'on',
    roundedSelection: true,
    scrollbar: {
      verticalScrollbarSize: 6,
      horizontalScrollbarSize: 6
    }
  })

  editor.onDidChangeModelContent(() => {
    emit('update:modelValue', editor.getValue())
  })
})

watch(() => props.language, (lang) => {
  if (editor) {
    monaco.editor.setModelLanguage(editor.getModel(), languageMap[lang] || 'plaintext')
  }
})

watch(() => props.modelValue, (val) => {
  if (editor && val !== editor.getValue()) {
    editor.setValue(val)
  }
})

function triggerUpload() {
  fileInput.value.click()
}

function onFileChange(e) {
  const file = e.target.files[0]
  if (!file) return

  const reader = new FileReader()
  reader.onload = (evt) => {
    const content = evt.target.result
    emit('update:modelValue', content)
    if (!props.language) {
      detectLang(content)
    }
  }
  reader.readAsText(file)
  e.target.value = ''
}

async function detectLang(code) {
  detecting.value = true
  try {
    const res = await detectLanguage(code)
    if (res.data.language !== 'plaintext') {
      emit('update:language', res.data.language)
    }
  } catch (e) {
    console.error(e)
  } finally {
    detecting.value = false
  }
}

function onLanguageUpdate(val) {
  emit('update:language', val)
}

function onLanguageChange() {
  if (!props.language && editor) {
    detectLang(editor.getValue())
  }
}

defineExpose({ editor })
</script>

<style scoped>
.editor-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
  overflow: hidden;
  border: 1px solid var(--border-light);
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid var(--border-light);
  background: var(--bg-subtle);
  gap: 12px;
  flex-wrap: wrap;
}
.toolbar-left {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}
.toolbar-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin-right: 4px;
}

.editor-container {
  flex: 1;
  min-height: 300px;
}

.detecting-tip {
  position: absolute;
  top: 64px;
  right: 24px;
  background: var(--brand-gradient);
  color: #fff;
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 6px;
  box-shadow: var(--shadow-brand);
  z-index: 10;
}

.spin {
  animation: spin 1s linear infinite;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}

@media (max-width: 768px) {
  .toolbar {
    padding: 10px 12px;
  }
  .toolbar-label {
    display: none;
  }
}
</style>

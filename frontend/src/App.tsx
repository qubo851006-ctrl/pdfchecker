import { useState } from 'react'
import UploadZone from './components/UploadZone'
import CheckReport from './components/CheckReport'
import { checkPdf, type CheckResult } from './api/check'
import styles from './App.module.css'

type State = 'idle' | 'checking' | 'done' | 'error'

export default function App() {
  const [state, setState] = useState<State>('idle')
  const [result, setResult] = useState<CheckResult | null>(null)
  const [error, setError] = useState('')
  const [filename, setFilename] = useState('')

  async function handleFile(file: File) {
    setFilename(file.name)
    setState('checking')
    setError('')
    try {
      const res = await checkPdf(file)
      setResult(res)
      setState('done')
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : '未知错误')
      setState('error')
    }
  }

  function reset() {
    setState('idle')
    setResult(null)
    setError('')
    setFilename('')
  }

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <h1 className={styles.title}>暗标格式检查工具</h1>
        <p className={styles.subtitle}>自动检测投标文件技术标（暗标）是否符合编制要求</p>
      </header>

      <main className={styles.main}>
        {state === 'idle' && (
          <UploadZone onFile={handleFile} disabled={false} />
        )}

        {state === 'checking' && (
          <div className={styles.checking}>
            <div className={styles.spinner} />
            <p>正在检查 <strong>{filename}</strong>…</p>
            <p className={styles.checkingHint}>AI 扫描身份信息可能需要约 10–30 秒</p>
          </div>
        )}

        {state === 'done' && result && (
          <CheckReport result={result} onReset={reset} />
        )}

        {state === 'error' && (
          <div className={styles.errorBox}>
            <p className={styles.errorTitle}>检查失败</p>
            <p className={styles.errorMsg}>{error}</p>
            <button className={styles.retryBtn} onClick={reset}>重试</button>
          </div>
        )}
      </main>

      <footer className={styles.footer}>
        暗标检查 · 仅供参考，最终以评标委员会审查为准
      </footer>
    </div>
  )
}

import { useRef, useState, DragEvent, ChangeEvent } from 'react'
import styles from './UploadZone.module.css'

interface Props {
  onFile: (file: File) => void
  disabled: boolean
}

export default function UploadZone({ onFile, disabled }: Props) {
  const inputRef = useRef<HTMLInputElement>(null)
  const [dragging, setDragging] = useState(false)

  function handleDrop(e: DragEvent) {
    e.preventDefault()
    setDragging(false)
    const file = e.dataTransfer.files[0]
    if (file && file.name.toLowerCase().endsWith('.pdf')) onFile(file)
  }

  function handleChange(e: ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    if (file) onFile(file)
    e.target.value = ''
  }

  return (
    <div
      className={`${styles.zone} ${dragging ? styles.dragging : ''} ${disabled ? styles.disabled : ''}`}
      onClick={() => !disabled && inputRef.current?.click()}
      onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
      onDragLeave={() => setDragging(false)}
      onDrop={handleDrop}
    >
      <input
        ref={inputRef}
        type="file"
        accept=".pdf"
        hidden
        onChange={handleChange}
        disabled={disabled}
      />
      <div className={styles.icon}>📄</div>
      <p className={styles.primary}>点击或拖拽 PDF 文件到此处</p>
      <p className={styles.hint}>仅支持 PDF 格式，最大 50MB</p>
    </div>
  )
}

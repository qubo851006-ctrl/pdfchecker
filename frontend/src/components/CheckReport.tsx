import { useState } from 'react'
import type { CheckResult, CheckItem } from '../api/check'
import styles from './CheckReport.module.css'

interface Props {
  result: CheckResult
  onReset: () => void
}

function ItemRow({ item }: { item: CheckItem }) {
  const [expanded, setExpanded] = useState(!item.passed)

  return (
    <div className={`${styles.item} ${item.passed ? styles.pass : styles.fail}`}>
      <div className={styles.itemHeader} onClick={() => setExpanded(v => !v)}>
        <span className={styles.badge}>{item.passed ? '✓ 通过' : '✗ 不通过'}</span>
        <span className={styles.label}>{item.label}</span>
        <span className={styles.detail}>{item.detail}</span>
        {item.violations.length > 0 && (
          <span className={styles.toggle}>{expanded ? '▲' : '▼'}</span>
        )}
      </div>
      {expanded && item.violations.length > 0 && (
        <ul className={styles.violations}>
          {item.violations.map((v, i) => (
            <li key={i}>{v}</li>
          ))}
        </ul>
      )}
    </div>
  )
}

export default function CheckReport({ result, onReset }: Props) {
  return (
    <div className={styles.wrapper}>
      <div className={`${styles.verdict} ${result.overall_passed ? styles.verdictPass : styles.verdictFail}`}>
        <div className={styles.verdictIcon}>{result.overall_passed ? '✅' : '❌'}</div>
        <div>
          <div className={styles.verdictTitle}>{result.verdict}</div>
          <div className={styles.verdictFile}>{result.filename}</div>
        </div>
      </div>

      <div className={styles.checks}>
        {result.checks.map(item => (
          <ItemRow key={item.key} item={item} />
        ))}
      </div>

      <button className={styles.resetBtn} onClick={onReset}>
        检查另一个文件
      </button>
    </div>
  )
}

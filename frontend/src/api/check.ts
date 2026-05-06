export interface CheckItem {
  key: string
  label: string
  passed: boolean
  detail: string
  violations: string[]
}

export interface CheckResult {
  filename: string
  overall_passed: boolean
  verdict: string
  checks: CheckItem[]
}

export async function checkPdf(file: File): Promise<CheckResult> {
  const form = new FormData()
  form.append('file', file)

  const resp = await fetch('/api/check', { method: 'POST', body: form })
  if (!resp.ok) {
    const err = await resp.json().catch(() => ({ detail: resp.statusText }))
    throw new Error(err.detail || '请求失败')
  }
  return resp.json()
}

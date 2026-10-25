// The dev server answers a missing /data/... file with the HTML page (status 200), so every JSON
// fetch must check the content type before parsing. Returns null for anything that is not JSON.
export function okJson(r) {
  if (!r || !r.ok) return null
  const ct = r.headers.get('content-type') || ''
  if (!ct.includes('json')) return null
  return r.json().catch(() => null)
}

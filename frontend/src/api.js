const API = import.meta.env.VITE_API_BASE_URL || ''
const response = async (request) => {
  const res = await request
  if (!res.ok) { const body = await res.json().catch(() => ({})); throw new Error(body.detail || 'Request failed.') }
  return res
}
export const api = {
  statistics: () => response(fetch(`${API}/api/statistics`)).then(r => r.json()),
  analyses: () => response(fetch(`${API}/api/analyses`)).then(r => r.json()),
  analysis: id => response(fetch(`${API}/api/analyses/${id}`)).then(r => r.json()),
  analyze: form => response(fetch(`${API}/api/analyze`, { method: 'POST', body: form })).then(r => r.json()),
  report: (id, type) => `${API}/api/reports/${id}/${type}`,
  imageUrl: path => {
    if (!path) return ''
    const normalized = path.replaceAll('\\', '/')
    const relativePath = normalized.split('/storage/')[1]
    return relativePath ? `${API}/storage/${relativePath}` : ''
  }
}

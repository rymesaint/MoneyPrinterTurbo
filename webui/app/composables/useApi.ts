const API_BASE = '/api/v1'

export function useApi() {
  async function request(method: string, path: string, body?: any) {
    const opts: RequestInit = {
      method,
      headers: { 'Content-Type': 'application/json' },
    }
    if (body) opts.body = JSON.stringify(body)
    const res = await fetch(`${API_BASE}${path}`, opts)
    return res.json()
  }

  const get = (path: string) => request('GET', path)
  const post = (path: string, body?: any) => request('POST', path, body)
  const del = (path: string) => request('DELETE', path)

  return {
    // Config
    getConfig: () => get('/config'),
    saveConfig: (data: any) => post('/config', data),

    // Fonts & Voices
    getFonts: () => get('/fonts'),
    getVoices: (ttsServer: string) => get(`/voices?tts_server=${encodeURIComponent(ttsServer)}`),
    previewVoice: (data: any) => post('/voice/preview', data),

    // LLM
    generateScript: (data: any) => post('/scripts', data),
    generateTerms: (data: any) => post('/terms', data),

    // Video Tasks
    createVideo: (data: any) => post('/videos', data),
    createSubtitle: (data: any) => post('/subtitle', data),
    createAudio: (data: any) => post('/audio', data),
    getTasks: (page = 1, pageSize = 10) => get(`/tasks?page=${page}&page_size=${pageSize}`),
    getTask: (taskId: string) => get(`/tasks/${taskId}`),
    deleteTask: (taskId: string) => del(`/tasks/${taskId}`),

    // Music & Materials
    getBgmList: () => get('/musics'),
    getVideoMaterials: () => get('/video_materials'),

    // Raw fetch for file uploads and streaming
    uploadFile: async (file: File) => {
      const fd = new FormData()
      fd.append('file', file)
      const res = await fetch(`${API_BASE}/upload`, { method: 'POST', body: fd })
      return res.json()
    },

    // Task log streaming
    streamTaskLog: async function* (taskId: string) {
      const logUrl = `/tasks/${taskId}/task.log`
      let offset = 0
      while (true) {
        try {
          const res = await fetch(logUrl)
          if (res.ok) {
            const text = await res.text()
            if (text.length > offset) {
              yield text.slice(offset)
              offset = text.length
            }
          }
        } catch { /* ignore */ }
        await new Promise(r => setTimeout(r, 2000))
      }
    }
  }
}

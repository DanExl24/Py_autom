export const API_BASE = import.meta.env.VITE_API_URL 
  ? String(import.meta.env.VITE_API_URL).replace(/\/$/, '') 
  : ''

export const fichasApi = {
  async getFichas() {
    const res = await fetch(`${API_BASE}/api/fichas`)
    if (!res.ok) {
      throw new Error('No se pudieron obtener los datos de las fichas')
    }
    return res.json()
  },

  async abrirProgramador(fichaNum: string) {
    const res = await fetch(`${API_BASE}/api/abrir-programador/${fichaNum}`)
    if (!res.ok) {
      const errData = await res.json().catch(() => ({}))
      throw new Error(errData.detail || 'Ficha no encontrada en Drive')
    }
    return res.json()
  },

  async abrirBuscadorGui() {
    const res = await fetch(`${API_BASE}/api/abrir-buscador-gui`, { method: 'POST' })
    if (!res.ok) {
      throw new Error('No se pudo lanzar la interfaz flotante')
    }
    return res.json()
  },

  async fetchActualizarStream(driveToken?: string | null) {
    const headers: Record<string, string> = {}
    if (driveToken) {
      headers['X-Google-Access-Token'] = driveToken
    }

    return fetch(`${API_BASE}/api/actualizar`, {
      method: 'POST',
      headers
    })
  }
}

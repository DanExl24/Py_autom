export const fichasApi = {
  async getFichas() {
    const res = await fetch('/api/fichas')
    if (!res.ok) {
      throw new Error('No se pudieron obtener los datos de las fichas')
    }
    return res.json()
  },

  async abrirBuscadorGui() {
    const res = await fetch('/api/abrir-buscador-gui', { method: 'POST' })
    if (!res.ok) {
      throw new Error('No se pudo lanzar la interfaz flotante')
    }
    return res.json()
  }
}

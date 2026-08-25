import { ref, computed } from 'vue'
import type { Ficha, Kpis } from '../types'
import { fichasApi } from '../services/fichasApi'

const normalizeTrimestreJS = (str: string): string => {
  if (!str) return str
  const s = str.trim().toUpperCase()
  const match = s.match(/T\s*-\s*(I{1,3}|IV|V)\s*[-/ ]\s*(\d{4})/)
  if (match) {
    return `T-${match[1]}-${match[2]}`
  }
  return s
}

export function useFichas() {
  const rawFichas = ref<Ficha[]>([])
  const loading = ref(true)
  const error = ref<string | null>(null)

  const loadData = async (silent = false) => {
    try {
      if (!silent) {
        loading.value = true
        error.value = null
      }
      const data = await fichasApi.getFichas()
      
      const list: Ficha[] = []
      
      // Procesar la estructura Red -> Ficha -> Info
      for (const [redNombre, fichasDict] of Object.entries(data)) {
        for (const [fichaNum, info] of Object.entries(fichasDict as any)) {
          const infoObj = info as any
          
          // Calcular duración si es nula
          let duracionCalculada = 0
          const duracion = infoObj.DURACION
          if (duracion === null || duracion === undefined || duracion === "") {
            const start = infoObj["FECHA INICIO"] ? new Date(infoObj["FECHA INICIO"]) : null
            const end = infoObj["FECHA TERMINACION"] ? new Date(infoObj["FECHA TERMINACION"]) : null
            if (start && end && !isNaN(start.getTime()) && !isNaN(end.getTime())) {
              duracionCalculada = Math.round((end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24 * 30.44))
            }
          } else {
            duracionCalculada = parseInt(duracion) || 0
          }
          
          list.push({
            ...infoObj,
            FICHA: String(fichaNum),
            "RED DE CONOCIMIENTO": redNombre,
            "NOMBRE DEL PROGRAMA": String(infoObj["NOMBRE DEL PROGRAMA"] ?? ''),
            "MUNICIPIO": String(infoObj["MUNICIPIO"] ?? ''),
            "INSTRUCTOR TÉCNICO 2025": String(infoObj["INSTRUCTOR TÉCNICO 2025"] ?? ''),
            "INSTRUCTOR TÉCNICO 2026": String(infoObj["INSTRUCTOR TÉCNICO 2026"] ?? ''),
            "APOYO TÉCNICO INGLES": String(infoObj["APOYO TÉCNICO INGLES"] ?? ''),
            "TIPO DE OFERTA": String(infoObj["TIPO DE OFERTA"] ?? ''),
            NIVEL: String(infoObj.NIVEL ?? ''),
            "APRENDICES MATRICULADOS": parseInt(infoObj["APRENDICES MATRICULADOS"]) || 0,
            "CODIGO DE PROGRAMA": parseInt(infoObj["CODIGO DE PROGRAMA"]) || 0,
            VERSION: parseInt(infoObj.VERSION) || 1,
            "CÓDIGO PROYECTO": parseInt(infoObj["CÓDIGO PROYECTO"]) || 0,
            "AÑO /TRIMESTRE DE INICIO": normalizeTrimestreJS(infoObj["AÑO /TRIMESTRE DE INICIO"] || ''),
            DURACION_CALCULADA: duracionCalculada
          })
        }
      }
      rawFichas.value = list
    } catch (e: any) {
      if (!silent) {
        error.value = e.message || 'Error al conectar'
      } else {
        console.error('Silent refresh failed:', e)
      }
    } finally {
      if (!silent) {
        loading.value = false
      }
    }
  }

  // --- CÁLCULO DE KPIs ---
  const kpis = computed<Kpis>(() => {
    if (!rawFichas.value.length) {
      return {
        totalFormaciones: 0,
        totalAprendices: 0,
        promedioAprendices: 0,
        promedioDuracion: 0,
        totalRedes: 0,
        totalMunicipios: 0,
        totalInstructores: 0
      }
    }

    const totalFormaciones = rawFichas.value.length
    const totalAprendices = rawFichas.value.reduce((sum, f) => sum + f["APRENDICES MATRICULADOS"], 0)
    const promedioAprendices = Number((totalAprendices / totalFormaciones).toFixed(1))
    
    const duraciones = rawFichas.value.map(f => f.DURACION_CALCULADA).filter(Boolean)
    const promedioDuracion = duraciones.length 
      ? Number((duraciones.reduce((sum, d) => sum + d, 0) / duraciones.length).toFixed(1))
      : 0

    const redes = new Set(rawFichas.value.map(f => f["RED DE CONOCIMIENTO"]).filter(Boolean))
    const municipios = new Set(rawFichas.value.map(f => f.MUNICIPIO).filter(Boolean))
    
    const instructores = new Set<string>()
    rawFichas.value.forEach(f => {
      const inst25 = f["INSTRUCTOR TÉCNICO 2025"]
      const inst26 = f["INSTRUCTOR TÉCNICO 2026"]
      if (inst25 && inst25 !== 'None' && inst25.trim()) instructores.add(inst25.trim().toUpperCase())
      if (inst26 && inst26 !== 'None' && inst26.trim()) instructores.add(inst26.trim().toUpperCase())
    })

    return {
      totalFormaciones,
      totalAprendices,
      promedioAprendices,
      promedioDuracion,
      totalRedes: redes.size,
      totalMunicipios: municipios.size,
      totalInstructores: instructores.size
    }
  })

  const proximoInicio = computed(() => {
    const hoy = new Date()
    const futuros = rawFichas.value
      .filter(f => f["FECHA INICIO"])
      .map(f => ({ fecha: new Date(f["FECHA INICIO"]), str: f["FECHA INICIO"] }))
      .filter(item => !isNaN(item.fecha.getTime()) && item.fecha >= hoy)
      .sort((a, b) => a.fecha.getTime() - b.fecha.getTime())
      
    return futuros.length ? futuros[0].str : 'No programado'
  })

  const proximaFinalizacion = computed(() => {
    const hoy = new Date()
    const futuros = rawFichas.value
      .filter(f => f["FECHA TERMINACION"])
      .map(f => ({ fecha: new Date(f["FECHA TERMINACION"]), str: f["FECHA TERMINACION"] }))
      .filter(item => !isNaN(item.fecha.getTime()) && item.fecha >= hoy)
      .sort((a, b) => a.fecha.getTime() - b.fecha.getTime())
      
    return futuros.length ? futuros[0].str : 'No programada'
  })

  // --- ALERTAS DEL DASHBOARD ---
  const alertBajaMatricula = computed(() => {
    return rawFichas.value.filter(f => f["APRENDICES MATRICULADOS"] < 15).length
  })

  const alertProximasTerminar = computed(() => {
    const hoy = new Date()
    const limite = new Date()
    limite.setDate(limite.getDate() + 30) // 30 días
    
    return rawFichas.value.filter(f => {
      if (!f["FECHA TERMINACION"]) return false
      const term = new Date(f["FECHA TERMINACION"])
      return !isNaN(term.getTime()) && term >= hoy && term <= limite
    }).length
  })

  const alertSinProyecto = computed(() => {
    return rawFichas.value.filter(f => !f["CÓDIGO PROYECTO"] || f["CÓDIGO PROYECTO"] === 0).length
  })

  return {
    rawFichas,
    loading,
    error,
    loadData,
    kpis,
    proximoInicio,
    proximaFinalizacion,
    alertBajaMatricula,
    alertProximasTerminar,
    alertSinProyecto
  }
}

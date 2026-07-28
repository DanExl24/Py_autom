import type { Ficha } from '../types'

/**
 * Interface para la información agrupada por horario
 */
export interface HorarioGrupo {
  horario: string
  jornada: string
  count: number
  totalAprendices: number
  fichas: Ficha[]
}

/**
 * Normaliza una cadena de horario eliminando espacios extra y limpiando formato
 */
export function normalizeHorario(str?: string | null): string {
  if (!str || !str.trim()) return 'NO REGISTRADO'
  return str.trim().replace(/\s+/g, ' ').toUpperCase()
}

/**
 * Infiere la jornada a partir de una cadena de horario.
 * Si el horario posee múltiples bloques o días distintos (horario compuesto), retorna "Horario Compuesto".
 */
export function inferJornada(horarioStr?: string | null): string {
  if (!horarioStr || !horarioStr.trim()) return 'No registrada'
  
  const text = horarioStr.toUpperCase().trim()

  // Detectar horarios compuestos (múltiples rangos de horas o múltiples bloques con 'Y', saltos de línea o múltiples rangos "A" / "-")
  // Buscar todas las ocurrencias de horas del tipo HH:MM o H:MM o HH AM/PM
  const rangeMatches = text.match(/\b\d{1,2}(?::\d{2})?\s*(?:AM|PM)?\s*(?:-|A|HASTA)\s*\d{1,2}(?::\d{2})?\s*(?:AM|PM)?\b/gi) || []
  
  if (rangeMatches.length > 1 || text.includes('\n') || (text.includes(' SÁBADO') && text.includes(' LUNES')) || text.includes(' Y ')) {
    return 'Horario Compuesto'
  }

  // 1. Verificación por palabra clave explícita en el texto
  if (text.includes('MAÑANA') || text.includes('DIURNA')) return 'Mañana'
  if (text.includes('TARDE')) return 'Tarde'
  if (text.includes('MIXTA')) return 'Mixta'
  if (text.includes('NOCHE') || text.includes('NOCTURNA')) return 'Noche'

  // 2. Extraer rango de horas numérico
  const timeMatch = text.match(/(\d{1,2})(?::(\d{2}))?\s*(AM|PM)?\s*(?:-|A|HASTA)\s*(\d{1,2})(?::(\d{2}))?\s*(AM|PM)?/i)

  if (timeMatch) {
    let startHour = parseInt(timeMatch[1], 10)
    const startAmPm = timeMatch[3] ? timeMatch[3].toUpperCase() : null
    let endHour = parseInt(timeMatch[4], 10)
    const endAmPm = timeMatch[6] ? timeMatch[6].toUpperCase() : null

    // Ajustar AM/PM si está especificado
    if (startAmPm === 'PM' && startHour < 12) startHour += 12
    if (startAmPm === 'AM' && startHour === 12) startHour = 0

    if (endAmPm === 'PM' && endHour < 12) endHour += 12
    if (endAmPm === 'AM' && endHour === 12) endHour = 0

    // Si la hora final es 12..20 y start es 12..14 sin AM/PM explícito, es probable 24h
    // Evaluación por rangos según requerimiento:
    // Mañana: 6am - 14pm (06:00 - 14:00)
    // Tarde: 12pm - 20pm (12:00 - 20:00)
    // Mixta: 16pm - 23:59pm (16:00 - 23:59)
    // Noche: 18pm - 23:59pm (18:00 - 23:59)

    // Evaluar coincidencia de rangos
    if (startHour >= 6 && endHour <= 14 && startHour < 12) {
      return 'Mañana'
    }
    if (startHour >= 12 && endHour <= 20 && startHour < 16) {
      return 'Tarde'
    }
    if (startHour >= 16 && startHour < 18) {
      return 'Mixta'
    }
    if (startHour >= 18) {
      return 'Noche'
    }

    // Fallback por inicio de hora
    if (startHour >= 6 && startHour < 12) return 'Mañana'
    if (startHour >= 12 && startHour < 16) return 'Tarde'
    if (startHour >= 16 && startHour < 18) return 'Mixta'
    if (startHour >= 18) return 'Noche'
  }

  return 'Sin especificar'
}

/**
 * Agrupa fichas por horario normalizado y calcula estadísticas
 */
export function getHorariosGrouped(fichas: Ficha[]): HorarioGrupo[] {
  const map = new Map<string, { horario: string; jornada: string; fichas: Ficha[]; totalAprendices: number }>()

  for (const f of fichas) {
    const raw = f.HORARIO ? f.HORARIO.trim() : 'SIN HORARIO REGISTRADO'
    const key = normalizeHorario(raw)
    
    if (!map.has(key)) {
      map.set(key, {
        horario: raw,
        jornada: inferJornada(raw),
        fichas: [],
        totalAprendices: 0
      })
    }

    const grupo = map.get(key)!
    grupo.fichas.push(f)
    grupo.totalAprendices += f["APRENDICES MATRICULADOS"] || 0
  }

  return Array.from(map.values())
    .map(g => ({
      horario: g.horario,
      jornada: g.jornada,
      count: g.fichas.length,
      totalAprendices: g.totalAprendices,
      fichas: g.fichas
    }))
    .sort((a, b) => b.count - a.count)
}

/**
 * Filtra fichas por criterios de Horario, Jornada y Rango de Fechas
 */
export function filterFichasByHorario(
  fichas: Ficha[],
  options: {
    jornada?: string
    horario?: string
    fechaDesde?: string
    fechaHasta?: string
  }
): Ficha[] {
  const { jornada, horario, fechaDesde, fechaHasta } = options

  return fichas.filter(f => {
    // Filtro por Jornada
    if (jornada && jornada !== 'Todas') {
      const jInferida = inferJornada(f.HORARIO)
      if (jInferida !== jornada) return false
    }

    // Filtro por Horario especifico
    if (horario && horario !== 'Todos') {
      if (normalizeHorario(f.HORARIO) !== normalizeHorario(horario)) return false
    }

    // Filtro por Fechas (FECHA INICIO / FECHA TERMINACION)
    if (fechaDesde) {
      if (!f["FECHA INICIO"] || f["FECHA INICIO"] < fechaDesde) return false
    }
    if (fechaHasta) {
      if (!f["FECHA TERMINACION"] || f["FECHA TERMINACION"] > fechaHasta) return false
    }

    return true
  })
}

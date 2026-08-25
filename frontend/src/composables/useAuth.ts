import { ref, computed } from 'vue'
import type { AuthUser } from '../types'

const user = ref<AuthUser | null>(null)
const token = ref<string | null>(null)
const driveAccessToken = ref<string | null>(localStorage.getItem('google_drive_token'))

// Función para decodificar JWT sin librerías externas
function parseJwt(tokenStr: string): any {
  try {
    const base64Url = tokenStr.split('.')[1]
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/')
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    )
    return JSON.parse(jsonPayload)
  } catch (e) {
    console.error('Error al decodificar token JWT:', e)
    return null
  }
}

// Cargar sesión inicial desde localStorage
const savedUser = localStorage.getItem('auth_user')
const savedToken = localStorage.getItem('auth_token')
if (savedUser && savedToken) {
  try {
    user.value = JSON.parse(savedUser)
    token.value = savedToken
  } catch (e) {
    localStorage.removeItem('auth_user')
    localStorage.removeItem('auth_token')
  }
}

export function useAuth() {
  const isAuthenticated = computed(() => !!user.value)

  const loginWithGoogleCredential = (credential: string) => {
    const payload = parseJwt(credential)
    if (!payload || !payload.email) {
      throw new Error('Token de Google no válido o sin correo electrónico.')
    }

    const authUser: AuthUser = {
      email: payload.email,
      name: payload.name || payload.email.split('@')[0],
      picture: payload.picture,
      sub: payload.sub
    }

    user.value = authUser
    token.value = credential

    localStorage.setItem('auth_user', JSON.stringify(authUser))
    localStorage.setItem('auth_token', credential)
  }

  const logout = () => {
    user.value = null
    token.value = null
    driveAccessToken.value = null
    localStorage.removeItem('auth_user')
    localStorage.removeItem('auth_token')
    localStorage.removeItem('google_drive_token')
  }

  // Solicitar o renovar Token OAuth para Google Drive desde el navegador
  const requestDriveAccessToken = (forcePrompt = false): Promise<string> => {
    return new Promise((resolve, reject) => {
      const google = (window as any).google
      const clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID

      if (!clientId) {
        reject(new Error('VITE_GOOGLE_CLIENT_ID no está configurado en las variables de entorno.'))
        return
      }

      if (!google || !google.accounts || !google.accounts.oauth2) {
        reject(new Error('Google Identity Services no está listo en el navegador. Recarga la página e intenta de nuevo.'))
        return
      }

      try {
        const client = google.accounts.oauth2.initTokenClient({
          client_id: clientId,
          scope: 'https://www.googleapis.com/auth/drive.readonly https://www.googleapis.com/auth/spreadsheets.readonly',
          callback: (tokenResponse: any) => {
            if (tokenResponse && tokenResponse.access_token) {
              driveAccessToken.value = tokenResponse.access_token
              localStorage.setItem('google_drive_token', tokenResponse.access_token)
              resolve(tokenResponse.access_token)
            } else if (tokenResponse && tokenResponse.error) {
              reject(new Error(tokenResponse.error_description || tokenResponse.error))
            } else {
              reject(new Error('No se concedieron permisos de Google Drive.'))
            }
          },
          error_callback: (err: any) => {
            reject(new Error(err.message || 'Error al conectar con Google OAuth.'))
          }
        })

        client.requestAccessToken({ prompt: forcePrompt ? 'consent' : '' })
      } catch (err: any) {
        reject(err)
      }
    })
  }

  return {
    user,
    token,
    driveAccessToken,
    isAuthenticated,
    loginWithGoogleCredential,
    requestDriveAccessToken,
    logout
  }
}

import { ref, computed } from 'vue'
import type { AuthUser } from '../types'

const user = ref<AuthUser | null>(null)
const token = ref<string | null>(null)

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
    localStorage.removeItem('auth_user')
    localStorage.removeItem('auth_token')
  }

  return {
    user,
    token,
    isAuthenticated,
    loginWithGoogleCredential,
    logout
  }
}

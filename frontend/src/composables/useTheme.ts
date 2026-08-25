import { ref, onMounted } from 'vue'

export function useTheme() {
  const isDark = ref(false)

  const applyTheme = (dark: boolean) => {
    isDark.value = dark
    if (dark) {
      document.documentElement.classList.add('dark')
      localStorage.setItem('theme', 'dark')
    } else {
      document.documentElement.classList.remove('dark')
      localStorage.setItem('theme', 'light')
    }
  }

  const toggleDarkMode = () => {
    applyTheme(!isDark.value)
  }

  const initTheme = () => {
    const savedTheme = localStorage.getItem('theme')
    const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
    if (savedTheme === 'dark' || (!savedTheme && systemPrefersDark)) {
      applyTheme(true)
    } else {
      applyTheme(false)
    }
  }

  onMounted(() => {
    initTheme()
  })

  return {
    isDark,
    toggleDarkMode,
    initTheme
  }
}

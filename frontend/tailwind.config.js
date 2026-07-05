/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: {
          light: '#2B5784',
          DEFAULT: '#1E3A5F', // Azul Petróleo
          dark: '#112239',
        },
        secondary: {
          DEFAULT: '#2563EB', // Azul
        },
        success: {
          DEFAULT: '#10B981', // Verde Esmeralda
        },
        warning: {
          DEFAULT: '#F59E0B', // Ámbar
        },
        danger: {
          DEFAULT: '#EF4444', // Rojo
        },
        slate: {
          950: '#0B0F19' // Fondo oscuro premium azulado
        }
      }
    },
  },
  plugins: [],
}

/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        cream: '#FAF8F4',
        ink: '#171B19',
        linea: '#E4E0D6',
        oro: '#B8893B',
        verde: {
          DEFAULT: '#2E6B4A',
          profundo: '#0F2E1F',
          claro: '#E9F4EC',
        },
      },
      fontFamily: {
        sans: ['Segoe UI', 'system-ui', 'Arial', 'sans-serif'],
      },
    },
  },
  plugins: [],
}

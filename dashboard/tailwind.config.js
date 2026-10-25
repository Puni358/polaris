/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  safelist: [
    { pattern: /(bg|border|text)-(emerald|amber|rose|zinc|cyan|violet)-(400|700|800|950)/ },
    { pattern: /(bg)-(emerald|amber|rose|zinc)-950\/40/ },
  ],
  theme: {
    extend: {
      colors: {
        scada: {
          bg: '#09090b',
          panel: '#121214',
          panel2: '#17171a',
          border: '#27272a',
        },
      },
      fontFamily: {
        mono: ['"JetBrains Mono"', '"Geist Mono"', 'ui-monospace', 'monospace'],
        sans: ['Inter', 'ui-sans-serif', 'system-ui'],
      },
    },
  },
  plugins: [],
}

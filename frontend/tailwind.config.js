/** @type {import('tailwindcss').Config} */
// Tokens mapeados para variáveis CSS definidas em src/styles.scss (paleta do sistema:
// azul marca / verde sucesso / vermelho destaque-perigo / cinzas neutros).
// Regra do projeto: estilização via Tailwind; SCSS apenas global. Ver specs/06-frontend-album.
module.exports = {
  content: ['./src/**/*.{html,ts}'],
  darkMode: 'class',
  theme: {
    // Breakpoints alinhados ao QA obrigatório (360 / 768 / 1440). Mobile-first.
    screens: {
      sm: '480px',
      md: '768px',
      lg: '1024px',
      xl: '1440px',
    },
    extend: {
      colors: {
        canvas: 'var(--canvas)',
        surface: 'var(--surface)',
        'surface-2': 'var(--surface-2)',
        ink: 'var(--ink)',
        muted: 'var(--muted)',
        border: 'var(--border)',
        brand: {
          50: 'var(--brand-50)',
          500: 'var(--brand-500)',
          600: 'var(--brand-600)',
          700: 'var(--brand-700)',
        },
        accent: {
          50: 'var(--accent-50)',
          400: 'var(--accent-400)',
          500: 'var(--accent-500)',
          600: 'var(--accent-600)',
        },
        success: {
          50: 'var(--success-50)',
          500: 'var(--success-500)',
          600: 'var(--success-600)',
          700: 'var(--success-700)',
        },
        danger: 'var(--danger)',
      },
      fontFamily: {
        display: ['"Barlow Condensed"', '"Roboto Condensed"', '"Arial Narrow"', 'system-ui', 'sans-serif'],
        sans: ['Inter', 'system-ui', '-apple-system', '"Segoe UI"', 'Roboto', 'sans-serif'],
      },
      borderRadius: {
        card: '1rem',
      },
    },
  },
  plugins: [],
};

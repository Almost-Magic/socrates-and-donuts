/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // AMTL Theme
        midnight: {
          900: '#0A0E14', // bg-primary
          800: '#111720', // bg-secondary
          700: '#1A2030', // bg-tertiary
        },
        gold: {
          DEFAULT: '#C9944A',
          hover: '#D4A55B',
        },
      },
      fontFamily: {
        sans: ['-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
}

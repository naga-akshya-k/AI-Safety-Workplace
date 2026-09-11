/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        safety: {
          dark: '#0d1117',
          card: '#161b22',
          border: '#30363d',
          accent: '#238636',
          normal: '#238636',
          low: '#2f81f7',
          medium: '#d29922',
          high: '#db6d28',
          critical: '#f85149',
        }
      }
    },
  },
  plugins: [],
}

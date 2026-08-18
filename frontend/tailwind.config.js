/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        background: '#f8fafc',
        surface: '#ffffff',
        surfaceLight: '#f1f5f9',
        gov: {
          navy: '#002147',
          blue: '#0056b3',
          header: '#001529',
          saffron: '#d97706',
          green: '#15803d',
          border: '#cbd5e1',
          text: '#0f172a',
          muted: '#64748b'
        }
      },
      borderRadius: {
        'none': '0',
        'sm': '2px',
        DEFAULT: '4px',
        'md': '6px',
        'lg': '8px',
        'xl': '12px',
      }
    },
  },
  plugins: [],
}

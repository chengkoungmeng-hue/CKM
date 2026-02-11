/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
  theme: {
    extend: {
      colors: {
        primary: '#7F1D1D',      // 深紅 (更穩重)
        primaryLight: '#B91C1C', // 亮紅 (Hover用)
        gold: '#D4AF37',         // 經典金
        goldLight: '#FCD34D',    // 亮金
        dark: '#0F172A',         // 午夜藍黑 (比純黑更有質感)
        cream: '#FFFBF0',        // 奶油白 (背景用)
      },
      fontFamily: {
        heading: ['"Koulen"', 'cursive'],
        body: ['"Noto Sans Khmer"', 'sans-serif'],
      },
      backgroundImage: {
        'luxury-pattern': "url('https://www.transparenttextures.com/patterns/stardust.png')",
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
      },
      boxShadow: {
        'glow': '0 0 20px rgba(212, 175, 55, 0.3)',
      }
    },
  },
  plugins: [],
}

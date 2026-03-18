/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
  theme: {
    extend: {
      colors: {
        primary: '#7F1D1D',      // 深紅 (保留作為特定警示或印章點綴)
        primaryLight: '#B91C1C', // 亮红 
        gold: '#F59E0B',         // [校準] 完美對齊 Tailwind 的 amber-500，確保全站金屬色澤統一
        goldLight: '#FCD34D',    // [校準] 對齊 amber-300
        dark: '#0F172A',         // [校準] 完美對齊 slate-900 (午夜藍黑，極致奢華)
        cream: '#F8FAFC',        // [校準] 對齊 slate-50 (高冷白，取代偏黃的奶油色，讓白皮書更具智庫感)
      },
      fontFamily: {
        // [防禦升級] 建立由英至中、再至高棉文的「瀑布流降級矩陣」
        heading: ['"Playfair Display"', '"Noto Serif SC"', '"Hanuman"', 'serif'],
        body: ['system-ui', '-apple-system', '"PingFang SC"', '"Kantumruy Pro"', 'sans-serif'],
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        // [防禦升級] 拔除第三方外部網址，改用純 CSS 運算的奢華微光漸層 (可用於 Hover 特效)
        'luxury-shimmer': 'linear-gradient(110deg, rgba(255,255,255,0) 40%, rgba(255,255,255,0.1) 50%, rgba(255,255,255,0) 60%)',
      },
      boxShadow: {
        // [視覺微調] 降低透明度，擴散半徑，從刺眼的「發光」轉化為沉穩的「奢華微光」
        'glow': '0 0 30px rgba(245, 158, 11, 0.15)',
      }
    },
  },
  plugins: [],
}
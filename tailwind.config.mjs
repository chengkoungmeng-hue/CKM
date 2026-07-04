/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
  theme: {
    extend: {
      colors: {
        // Quiet Luxury Palette
        onyx: '#171717',        // 深瑪瑙黑 (取代 slate-900)
        champagne: '#C5A059',   // 香檳金 (取代 amber-600)
        'champagne-dark': '#8C6D31', // 深古銅金 (用於淺色背景的文字)
        pearl: '#FDFCF8',       // 珍珠米白 (取代 slate-50)
        
        // Legacy (Will be phased out)
        primary: '#7F1D1D',
        primaryLight: '#B91C1C',
        gold: '#F59E0B',
        goldLight: '#FCD34D',
        dark: '#0F172A',
        cream: '#F8FAFC',
      },
      fontFamily: {
        // [防禦升級] 建立由英至中、再至高棉文的「瀑布流降級矩陣」
        heading: ['"Playfair Display"', '"Noto Serif SC"', '"Hanuman"', 'serif'],
        body: ['system-ui', '-apple-system', '"PingFang SC"', 'sans-serif'],
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        // [防禦升級] 拔除第三方外部網址，改用純 CSS 運算的奢華微光漸層 (可用於 Hover 特效)
        'luxury-shimmer': 'linear-gradient(110deg, rgba(255,255,255,0) 40%, rgba(255,255,255,0.1) 50%, rgba(255,255,255,0) 60%)',
      },
      boxShadow: {
        // [視覺微調] 降低透明度，擴散半徑，從刺眼的「發光」轉化為沉穩的「奢華微光」 (Champagne Glow)
        'glow': '0 0 30px rgba(197, 160, 89, 0.15)',
        'glow-lg': '0 10px 40px rgba(197, 160, 89, 0.2)',
      }
    },
  },
  plugins: [],
}
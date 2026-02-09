/** @type {import('tailwindcss').Config} */
export default {
	content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
	theme: {
		extend: {
            colors: {
                primary: '#991B1B', // 更深沉穩重的紅色 (International Red)
                secondary: '#1F2937', // 深灰
                gold: '#D4AF37', // 奢華金
                cream: '#FDFBF7', // 背景米白 (比純白更有質感)
            },
            fontFamily: {
                heading: ['"Koulen"', 'cursive'],
                body: ['"Noto Sans Khmer"', 'sans-serif'],
            },
            backgroundImage: {
                'pattern': "url('https://www.transparenttextures.com/patterns/cubes.png')", // 增加背景紋理
            }
        },
	},
	plugins: [],
}

import { $ as $$Layout } from './Layout_C1i0rna2.mjs';
import { c as createComponent } from './consts_D4M2gLZs.mjs';
import 'piccolore';
import { r as renderComponent, a as renderTemplate, F as Fragment, m as maybeRenderHead, b as addAttribute } from './prerender_DYjHfg6U.mjs';
import { g as getCollection } from './_astro_content_OBtCAXZi.mjs';
import { $ as $$InsightCard } from './InsightCard_BRND59Bv.mjs';

async function getStaticPaths() {
  return [
    { params: { lang: "km" } },
    { params: { lang: "zh" } },
    { params: { lang: "en" } }
  ];
}
const $$Index = createComponent(async ($$result, $$props, $$slots) => {
  const Astro2 = $$result.createAstro($$props, $$slots);
  Astro2.self = $$Index;
  const { lang } = Astro2.params;
  const rawPosts = await getCollection("blog", ({ id, data }) => {
    return id.startsWith(`${lang}/`) && data.draft !== true;
  });
  rawPosts.sort((a, b) => b.id.localeCompare(a.id));
  const formatPost = (post) => {
    const slugParts = post.id.replace(/\.mdx?$/, "").split("/");
    const slug = slugParts.slice(1).join("/");
    return {
      title: post.data.title,
      subTitle: post.data.description,
      link: `/${lang}/blog/${slug}`,
      image: post.data.coverImage,
      category: post.data.category
    };
  };
  rawPosts.filter((p) => p.data.category === "pillar").map(formatPost);
  rawPosts.filter((p) => p.data.category === "trend").map(formatPost);
  const translations = {
    km: {
      title: "អត្ថបទ និងចំណេះដឹង",
      desc: "ព័ត៌មាន បទពិសោធន៍ និងនិន្នាការថ្មីៗនៃការរៀបចំម្ហូបការ",
      pillarTitle: "បទពិសោធន៍ និងក្បួនខ្នាតរៀបចំម្ហូបការ",
      trendTitle: "ព័ត៌មាន និងនិន្នាការថ្មីៗ",
      readMore: "អានបន្ថែម",
      homeUrl: "/"
    },
    zh: {
      title: "外燴指南與產業動態",
      desc: "深入了解 CKM 專業辦桌標準與最新婚宴趨勢",
      pillarTitle: "辦桌實戰指南",
      trendTitle: "產業最新動態",
      readMore: "閱讀更多",
      homeUrl: "/zh/"
    },
    en: {
      title: "Insights & Trends",
      desc: "Discover CKM's professional catering standards and the latest event trends",
      pillarTitle: "Professional Catering Guides",
      trendTitle: "Latest Trends & News",
      readMore: "Read More",
      homeUrl: "/en/"
    }
  };
  const t = translations[lang] || translations.en;
  return renderTemplate`${renderComponent($$result, "Layout", $$Layout, { "title": `${t.title} - CKM Premium Catering`, "description": t.desc, "lang": lang === "km" ? "km-KH" : lang === "zh" ? "zh-CN" : "en-US" }, { "default": async ($$result2) => renderTemplate`   ${maybeRenderHead()}<div${addAttribute(`w-full bg-slate-50 min-h-screen pt-24 pb-20 typo-${lang}`, "class")}> <div class="max-w-7xl mx-auto px-6"> <header class="text-center mb-16"> <h1 class="text-4xl md:text-5xl font-km-serif font-bold text-slate-900 mb-4">${t.title}</h1> <p class="text-slate-500 font-km-sans text-lg">${t.desc}</p> </header> <section> <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 md:gap-8"> ${rawPosts.map((post) => renderTemplate`${renderComponent($$result2, "InsightCard", $$InsightCard, { ...post, "titleClass": "text-lg md:text-xl font-km-serif font-bold text-slate-900 mb-2 md:mb-3 group-hover:text-amber-600 transition-colors duration-300 leading-snug", "subTitleClass": "text-slate-500 text-xs md:text-sm font-km-sans font-light mb-4 md:mb-6 leading-relaxed line-clamp-3", "linkClass": "mt-auto inline-flex items-center text-amber-600 text-xs md:text-sm font-km-sans font-medium hover:text-amber-700 transition-colors", "linkLabel": t.readMore }, { "link-icon": async ($$result3) => renderTemplate`<svg xmlns="http://www.w3.org/2000/svg" class="w-3 h-3 md:w-4 md:h-4 ml-2" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"></polyline></svg>` })}`)} </div> </section> </div> </div> `, "head": async ($$result2) => renderTemplate`${renderComponent($$result2, "Fragment", Fragment, { "slot": "head" }, { "default": async ($$result3) => renderTemplate` <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;0,700;1,600&family=Noto+Serif+SC:wght@600;700&family=Hanuman:wght@400;700&family=Kantumruy+Pro:wght@300;400;500&display=swap" rel="stylesheet"> ` })}` })}`;
}, "C:/Projects/CKM/src/pages/[lang]/blog/index.astro", void 0);

const $$file = "C:/Projects/CKM/src/pages/[lang]/blog/index.astro";
const $$url = "/[lang]/blog";

const _page = /*#__PURE__*/Object.freeze(/*#__PURE__*/Object.defineProperty({
    __proto__: null,
    default: $$Index,
    file: $$file,
    getStaticPaths,
    url: $$url
}, Symbol.toStringTag, { value: 'Module' }));

const page = () => _page;

export { page };

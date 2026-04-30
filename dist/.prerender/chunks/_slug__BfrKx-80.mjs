import { $ as $$Layout, a as $$Image } from './Layout_C1i0rna2.mjs';
import { c as createComponent } from './consts_D4M2gLZs.mjs';
import 'piccolore';
import { r as renderComponent, a as renderTemplate, F as Fragment, u as unescapeHTML, b as addAttribute, m as maybeRenderHead } from './prerender_DYjHfg6U.mjs';
import { g as getCollection, r as renderEntry } from './_astro_content_OBtCAXZi.mjs';

var __freeze = Object.freeze;
var __defProp = Object.defineProperty;
var __template = (cooked, raw) => __freeze(__defProp(cooked, "raw", { value: __freeze(cooked.slice()) }));
var _a;
async function getStaticPaths() {
  const blogEntries = await getCollection("blog");
  return blogEntries.map((entry) => {
    const entryId = entry.id.replace(/\.mdx?$/, "");
    const [lang, ...slugParts] = entryId.split("/");
    const slug = slugParts.join("/");
    return {
      params: { lang, slug },
      props: { entry }
    };
  });
}
const $$slug = createComponent(async ($$result, $$props, $$slots) => {
  const Astro2 = $$result.createAstro($$props, $$slots);
  Astro2.self = $$slug;
  const { lang, slug } = Astro2.params;
  const { entry } = Astro2.props;
  const { Content } = await renderEntry(entry);
  const allPostsRaw = await getCollection("blog");
  const allPosts = allPostsRaw.map((p) => ({ ...p, _slug: p.id.replace(/\.mdx?$/, "") })).filter((p) => p._slug.startsWith(`${lang}/`)).sort((a, b) => a._slug.localeCompare(b._slug));
  const entryIdClean = entry.id.replace(/\.mdx?$/, "");
  const currentIndex = allPosts.findIndex((p) => p._slug === entryIdClean);
  const prevPost = allPosts[currentIndex === 0 ? allPosts.length - 1 : currentIndex - 1];
  const nextPost = allPosts[currentIndex === allPosts.length - 1 ? 0 : currentIndex + 1];
  const prevSlug = prevPost?._slug.split("/").slice(1).join("/");
  const nextSlug = nextPost?._slug.split("/").slice(1).join("/");
  const { title, seoTitle, description, coverImage, targetGeo, authoritySignals } = entry.data;
  const baseUrl = "https://www.ckmkh.com";
  const currentUrl = `${baseUrl}/${lang}/blog/${slug}`;
  const absoluteCoverImage = `${baseUrl}/${lang}/blog/og/${slug}.png`;
  const homeUrl = lang === "km" ? "/" : `/${lang}/`;
  const mainPhone = "011 827 782";
  const telegramLink = "https://t.me/CKMSam06";
  const translations = {
    km: {
      tag: "កំណត់ហេតុប្រតិបត្តិការម្ហូបការ",
      author: "រៀបរៀងដោយ៖ ចុងភៅឯក ចេង គួងម៉េង",
      back: "ត្រឡប់ទៅទំព័រដើម",
      call: "ហៅទូរស័ព្ទឥឡូវនេះ",
      telegram: "ពិគ្រោះយោបល់",
      prev: "អត្ថបទមុន",
      next: "អត្ថបទបន្ទាប់"
    },
    zh: {
      tag: "办桌实战日志",
      author: "撰文：主厨 钟光明",
      back: "返回首页",
      call: "电话联系",
      telegram: "专人咨询",
      prev: "上一篇",
      next: "下一篇"
    },
    en: {
      tag: "Catering Operations Log",
      author: "By Executive Chef Cheng Koung Meng",
      back: "Return Home",
      call: "Call Now",
      telegram: "Consultation",
      prev: "Previous Post",
      next: "Next Post"
    }
  };
  const t = translations[lang] || translations.en;
  const formattedDate = entry.data.date ? entry.data.date.toLocaleDateString(
    lang === "km" ? "km-KH" : lang === "zh" ? "zh-CN" : "en-US",
    { year: "numeric", month: "long", day: "numeric" }
  ) : null;
  const articleSchema = JSON.stringify({
    "@context": "https://schema.org",
    "@type": "Article",
    headline: title,
    description,
    image: [absoluteCoverImage],
    author: {
      "@type": "Person",
      name: "Cheng Koung Meng"
    },
    datePublished: entry.data.date ? entry.data.date.toISOString().split("T")[0] : (/* @__PURE__ */ new Date()).toISOString().split("T")[0]
  });
  return renderTemplate`${renderComponent($$result, "Layout", $$Layout, { "title": seoTitle || title, "description": description, "image": absoluteCoverImage, "lang": lang }, { "default": async ($$result2) => renderTemplate`  ${maybeRenderHead()}<div${addAttribute(`bg-slate-50 min-h-[calc(100vh-80px)] py-10 md:py-16 selection:bg-amber-200 selection:text-slate-900 typo-${lang}`, "class")}> <article class="max-w-4xl mx-auto px-5 sm:px-8"> <header class="mb-10 text-center"> <div class="inline-block bg-slate-200 text-slate-700 px-4 py-1.5 rounded-sm text-xs font-bold tracking-widest uppercase mb-6 shadow-sm border border-slate-300"> ${t.tag} </div> <h1 class="text-3xl md:text-5xl font-bold mb-6 text-slate-900 leading-snug"> ${title} </h1> <div class="flex items-center justify-center gap-4 text-slate-500 text-sm py-3"> <span class="text-amber-600 font-bold tracking-wider uppercase">${t.author}</span> ${formattedDate && renderTemplate`${renderComponent($$result2, "Fragment", Fragment, {}, { "default": async ($$result3) => renderTemplate` <span class="text-slate-300">|</span> <time class="tracking-widest font-light">${formattedDate}</time> ` })}`} </div> </header> <div class="w-full aspect-[16/9] md:aspect-[21/9] overflow-hidden bg-slate-200 rounded-sm shadow-xl mb-12 border border-slate-200/60"> ${renderComponent($$result2, "Image", $$Image, { "src": coverImage, "alt": seoTitle || title, "width": 1200, "height": 675, "decoding": "async", "class": "w-full h-full object-cover", "loading": "eager" })} </div> <div class="flex flex-wrap justify-center gap-3 mb-12 border-b border-slate-200 pb-12"> ${authoritySignals && authoritySignals.map((signal) => renderTemplate`<span class="bg-white text-slate-700 px-4 py-2 text-sm font-bold border border-slate-200 shadow-sm rounded-sm"> <i class="fas fa-check-circle text-amber-500 mr-2"></i>${signal} </span>`)} </div> <div class="ckm-prose mx-auto bg-white p-6 md:p-16 rounded-sm shadow-md border border-slate-100"> ${renderComponent($$result2, "Content", Content, {})} </div> <div class="mt-16 flex flex-col md:flex-row items-center justify-center gap-4"> <a${addAttribute(`tel:+855${mainPhone.replace(/\s/g, "").substring(1)}`, "href")} class="hidden md:inline-flex items-center justify-center gap-3 bg-amber-500 hover:bg-amber-400 text-slate-950 px-10 py-4 min-h-[44px] rounded-sm font-bold tracking-widest uppercase transition-all duration-300 shadow-lg hover:shadow-xl focus:ring-2 focus:ring-amber-300 focus:outline-none"> <i class="fas fa-phone-alt"></i> ${t.call} </a> <a${addAttribute(telegramLink, "href")} target="_blank" rel="noopener noreferrer" class="hidden md:inline-flex items-center justify-center gap-3 bg-[#0088cc] hover:bg-[#007ab8] text-white px-10 py-4 min-h-[44px] rounded-sm font-bold tracking-widest uppercase transition-all duration-300 shadow-lg hover:shadow-xl focus:ring-2 focus:ring-[#0088cc] focus:outline-none"> <i class="fab fa-telegram-plane text-lg"></i> ${t.telegram} </a> <a${addAttribute(homeUrl, "href")} class="w-full md:w-auto inline-flex items-center justify-center gap-2 text-slate-500 hover:text-slate-900 px-6 py-4 min-h-[44px] rounded-sm font-bold tracking-widest uppercase transition-colors duration-300"> <i class="fas fa-arrow-left"></i> ${t.back} </a> </div> ${allPosts.length > 1 && renderTemplate`<div class="grid grid-cols-1 md:grid-cols-2 gap-4 mt-16 border-t border-slate-200 pt-10"> <a${addAttribute(`/${lang}/blog/${prevSlug}`, "href")} class="group flex flex-col items-start p-6 rounded-sm border border-slate-200 bg-white hover:bg-slate-800 hover:border-slate-800 transition-all duration-300 text-left cursor-pointer shadow-sm hover:shadow-lg"> <span class="text-xs font-bold tracking-widest text-slate-400 group-hover:text-amber-400 uppercase mb-2 transition-colors">← ${t.prev}</span> <span class="text-lg md:text-xl font-bold text-slate-800 group-hover:text-white transition-colors line-clamp-2 leading-snug">${prevPost?.data.title}</span> </a> <a${addAttribute(`/${lang}/blog/${nextSlug}`, "href")} class="group flex flex-col items-end p-6 rounded-sm border border-slate-200 bg-white hover:bg-slate-800 hover:border-slate-800 transition-all duration-300 text-right cursor-pointer shadow-sm hover:shadow-lg"> <span class="text-xs font-bold tracking-widest text-slate-400 group-hover:text-amber-400 uppercase mb-2 transition-colors">${t.next} →</span> <span class="text-lg md:text-xl font-bold text-slate-800 group-hover:text-white transition-colors line-clamp-2 leading-snug">${nextPost?.data.title}</span> </a> </div>`} </article> </div> `, "head": async ($$result2) => renderTemplate`${renderComponent($$result2, "Fragment", Fragment, { "slot": "head" }, { "default": async ($$result3) => renderTemplate(_a || (_a = __template([' <link rel="canonical"', '> <link rel="alternate" hreflang="km-KH"', '> <link rel="alternate" hreflang="zh-CN"', '> <link rel="alternate" hreflang="en-US"', '> <link rel="alternate" hreflang="x-default"', '> <meta name="geo.placename"', '> <link rel="preconnect" href="https://fonts.googleapis.com"> <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin> <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;0,700;1,600&family=Noto+Serif+SC:wght@600;700&family=Hanuman:wght@400;700&family=Kantumruy+Pro:wght@300;400;500&display=swap" rel="stylesheet"> <script type="application/ld+json">', "<\/script> "])), addAttribute(currentUrl, "href"), addAttribute(`${baseUrl}/km/blog/${slug}`, "href"), addAttribute(`${baseUrl}/zh/blog/${slug}`, "href"), addAttribute(`${baseUrl}/en/blog/${slug}`, "href"), addAttribute(`${baseUrl}/km/blog/${slug}`, "href"), addAttribute(targetGeo, "content"), unescapeHTML(articleSchema)) })}` })}`;
}, "C:/Projects/CKM/src/pages/[lang]/blog/[slug].astro", void 0);

const $$file = "C:/Projects/CKM/src/pages/[lang]/blog/[slug].astro";
const $$url = "/[lang]/blog/[slug]";

const _page = /*#__PURE__*/Object.freeze(/*#__PURE__*/Object.defineProperty({
  __proto__: null,
  default: $$slug,
  file: $$file,
  getStaticPaths,
  url: $$url
}, Symbol.toStringTag, { value: 'Module' }));

const page = () => _page;

export { page };

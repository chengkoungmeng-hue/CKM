import { c as createComponent } from './consts_D4M2gLZs.mjs';
import 'piccolore';
import { d as createRenderInstruction, A as AstroError, I as ImageMissingAlt, m as maybeRenderHead, b as addAttribute, s as spreadAttributes, a as renderTemplate, e as FontFamilyNotFound, u as unescapeHTML, c as renderSlot, f as renderHead, r as renderComponent } from './prerender_DYjHfg6U.mjs';
import { r as resolveSrc, i as isESMImportedImage, g as getImage$1 } from './deterministic-string_Ct1ofG0Q.mjs';
import '@astrojs/internal-helpers/remote';
import '@astrojs/internal-helpers/path';
import 'clsx';
import * as mime from 'mrmime';

async function renderScript(result, id) {
  const inlined = result.inlinedScripts.get(id);
  let content = "";
  if (inlined != null) {
    if (inlined) {
      content = `<script type="module">${inlined}</script>`;
    }
  } else {
    const resolved = await result.resolve(id);
    content = `<script type="module" src="${result.userAssetsBase ? (result.base === "/" ? "" : result.base) + result.userAssetsBase : ""}${resolved}"></script>`;
  }
  return createRenderInstruction({ type: "script", id, content });
}

const $$Image = createComponent(async ($$result, $$props, $$slots) => {
  const Astro2 = $$result.createAstro($$props, $$slots);
  Astro2.self = $$Image;
  const props = Astro2.props;
  if (props.alt === void 0 || props.alt === null) {
    throw new AstroError(ImageMissingAlt);
  }
  if (typeof props.width === "string") {
    props.width = Number.parseInt(props.width);
  }
  if (typeof props.height === "string") {
    props.height = Number.parseInt(props.height);
  }
  const layout = props.layout ?? imageConfig.layout ?? "none";
  if (layout !== "none") {
    props.layout ??= imageConfig.layout;
    props.fit ??= imageConfig.objectFit ?? "cover";
    props.position ??= imageConfig.objectPosition ?? "center";
  } else if (imageConfig.objectFit || imageConfig.objectPosition) {
    props.fit ??= imageConfig.objectFit;
    props.position ??= imageConfig.objectPosition;
  }
  const image = await getImage(props);
  const additionalAttributes = {};
  if (image.srcSet.values.length > 0) {
    additionalAttributes.srcset = image.srcSet.attribute;
  }
  const { class: className, ...attributes } = { ...additionalAttributes, ...image.attributes };
  return renderTemplate`${maybeRenderHead()}<img${addAttribute(image.src, "src")}${spreadAttributes(attributes)}${addAttribute(className, "class")}>`;
}, "C:/Projects/CKM/node_modules/astro/components/Image.astro", void 0);

const $$Picture = createComponent(async ($$result, $$props, $$slots) => {
  const Astro2 = $$result.createAstro($$props, $$slots);
  Astro2.self = $$Picture;
  const defaultFormats = ["webp"];
  const defaultFallbackFormat = "png";
  const specialFormatsFallback = ["gif", "svg", "jpg", "jpeg"];
  const { formats = defaultFormats, pictureAttributes = {}, fallbackFormat, ...props } = Astro2.props;
  if (props.alt === void 0 || props.alt === null) {
    throw new AstroError(ImageMissingAlt);
  }
  const scopedStyleClass = props.class?.match(/\bastro-\w{8}\b/)?.[0];
  if (scopedStyleClass) {
    if (pictureAttributes.class) {
      pictureAttributes.class = `${pictureAttributes.class} ${scopedStyleClass}`;
    } else {
      pictureAttributes.class = scopedStyleClass;
    }
  }
  const layout = props.layout ?? imageConfig.layout ?? "none";
  const useResponsive = layout !== "none";
  if (useResponsive) {
    props.layout ??= imageConfig.layout;
    props.fit ??= imageConfig.objectFit ?? "cover";
    props.position ??= imageConfig.objectPosition ?? "center";
  } else if (imageConfig.objectFit || imageConfig.objectPosition) {
    props.fit ??= imageConfig.objectFit;
    props.position ??= imageConfig.objectPosition;
  }
  for (const key in props) {
    if (key.startsWith("data-astro-cid")) {
      pictureAttributes[key] = props[key];
    }
  }
  const originalSrc = await resolveSrc(props.src);
  const optimizedImages = await Promise.all(
    formats.map(
      async (format) => await getImage({
        ...props,
        src: originalSrc,
        format,
        widths: props.widths,
        densities: props.densities
      })
    )
  );
  const clonedSrc = isESMImportedImage(originalSrc) ? (
    // @ts-expect-error - clone is a private, hidden prop
    originalSrc.clone ?? originalSrc
  ) : originalSrc;
  let resultFallbackFormat = fallbackFormat ?? defaultFallbackFormat;
  if (!fallbackFormat && isESMImportedImage(clonedSrc) && specialFormatsFallback.includes(clonedSrc.format)) {
    resultFallbackFormat = clonedSrc.format;
  }
  const fallbackImage = await getImage({
    ...props,
    format: resultFallbackFormat,
    widths: props.widths,
    densities: props.densities
  });
  const imgAdditionalAttributes = {};
  const sourceAdditionalAttributes = {};
  if (props.sizes) {
    sourceAdditionalAttributes.sizes = props.sizes;
  }
  if (fallbackImage.srcSet.values.length > 0) {
    imgAdditionalAttributes.srcset = fallbackImage.srcSet.attribute;
  }
  const { class: className, ...attributes } = {
    ...imgAdditionalAttributes,
    ...fallbackImage.attributes
  };
  return renderTemplate`${maybeRenderHead()}<picture${spreadAttributes(pictureAttributes)}> ${Object.entries(optimizedImages).map(([_, image]) => {
    const srcsetAttribute = props.densities || !props.densities && !props.widths && !useResponsive ? `${image.src}${image.srcSet.values.length > 0 ? ", " + image.srcSet.attribute : ""}` : image.srcSet.attribute;
    return renderTemplate`<source${addAttribute(srcsetAttribute, "srcset")}${addAttribute(mime.lookup(image.options.format ?? image.src) ?? `image/${image.options.format}`, "type")}${spreadAttributes(sourceAdditionalAttributes)}>`;
  })}  <img${addAttribute(fallbackImage.src, "src")}${spreadAttributes(attributes)}${addAttribute(className, "class")}> </picture>`;
}, "C:/Projects/CKM/node_modules/astro/components/Picture.astro", void 0);

const componentDataByCssVariable = new Map([]);

function filterPreloads(data, preload) {
  if (!preload) {
    return null;
  }
  if (preload === true) {
    return data;
  }
  return data.filter(
    ({ weight, style, subset }) => preload.some((p) => {
      if (p.weight !== void 0 && weight !== void 0 && !checkWeight(p.weight.toString(), weight)) {
        return false;
      }
      if (p.style !== void 0 && p.style !== style) {
        return false;
      }
      if (p.subset !== void 0 && p.subset !== subset) {
        return false;
      }
      return true;
    })
  );
}
function checkWeight(input, target) {
  const trimmedInput = input.trim();
  if (trimmedInput.includes(" ")) {
    return trimmedInput === target;
  }
  if (target.includes(" ")) {
    const [a, b] = target.split(" ");
    const parsedInput = Number.parseInt(input);
    return parsedInput >= Number.parseInt(a) && parsedInput <= Number.parseInt(b);
  }
  return input === target;
}

const $$Font = createComponent(($$result, $$props, $$slots) => {
  const Astro2 = $$result.createAstro($$props, $$slots);
  Astro2.self = $$Font;
  const { cssVariable, preload = false } = Astro2.props;
  const data = componentDataByCssVariable.get(cssVariable);
  if (!data) {
    throw new AstroError({
      ...FontFamilyNotFound,
      message: FontFamilyNotFound.message(cssVariable)
    });
  }
  const filteredPreloadData = filterPreloads(data.preloads, preload);
  return renderTemplate`<style>${unescapeHTML(data.css)}</style>${filteredPreloadData?.map(({ url, type }) => renderTemplate`<link rel="preload"${addAttribute(url, "href")} as="font"${addAttribute(`font/${type}`, "type")} crossorigin>`)}`;
}, "C:/Projects/CKM/node_modules/astro/components/Font.astro", void 0);

const assetQueryParams = undefined;
					const imageConfig = {"endpoint":{"route":"/_image"},"service":{"entrypoint":"astro/assets/services/sharp","config":{}},"domains":[],"remotePatterns":[],"responsiveStyles":false};
					Object.defineProperty(imageConfig, 'assetQueryParams', {
						value: assetQueryParams,
						enumerable: false,
						configurable: true,
					});
							const getImage = async (options) => await getImage$1(options, imageConfig);

const brandCkmLogoGold = new Proxy({"src":"/_astro/brand-ckm-logo-gold.B4TbdCfG.webp","width":400,"height":400,"format":"webp"}, {
						get(target, name, receiver) {
							if (name === 'clone') {
								return structuredClone(target);
							}
							if (name === 'fsPath') {
								return "C:/Projects/CKM/src/assets/images/home/brand-ckm-logo-gold.webp";
							}
							if (target[name] !== undefined && globalThis.astroAsset) globalThis.astroAsset?.referencedImages?.add("C:/Projects/CKM/src/assets/images/home/brand-ckm-logo-gold.webp");
							return target[name];
						}
					});

var __freeze = Object.freeze;
var __defProp = Object.defineProperty;
var __template = (cooked, raw) => __freeze(__defProp(cooked, "raw", { value: __freeze(cooked.slice()) }));
var _a;
const $$Layout = createComponent(($$result, $$props, $$slots) => {
  const Astro2 = $$result.createAstro($$props, $$slots);
  Astro2.self = $$Layout;
  const {
    title,
    description,
    image = "/open-graph.png",
    lang = "km"
  } = Astro2.props;
  const baseLang = lang.startsWith("km") ? "km" : lang.startsWith("zh") ? "zh" : "en";
  const homeUrl = baseLang === "km" ? "/" : `/${baseLang}/`;
  const siteDomain = "https://www.ckmkh.com";
  const canonicalURL = new URL(Astro2.url.pathname, Astro2.site || siteDomain);
  const ogImageAbsolute = image.startsWith("http") ? image : `${siteDomain}${image}`;
  const mainPhone = "011 827 782";
  const telegramLink = "https://t.me/CKMSam06";
  const cleanPhone = `+855${mainPhone.replace(/\s/g, "").substring(1)}`;
  const brandDict = {
    km: { title: "ចេង គួងម៉េង", subtitle: "សេវាកម្មម្ហូបការលំដាប់ខ្ពស់" },
    zh: { title: "CKM CATERING", subtitle: "PREMIUM SERVICE" },
    en: { title: "CKM CATERING", subtitle: "PREMIUM SERVICE" }
  };
  const brand = brandDict[baseLang];
  const navTranslations = {
    km: {
      service: "ស្តង់ដារប្រតិបត្តិការ",
      portfolio: "ម៉ឺនុយម្ហូបការ",
      insights: "កំណត់ហេតុ",
      contact: "ទាក់ទងយើង",
      call: "ហៅទូរស័ព្ទ",
      telegram: "Telegram",
      mooncake: "នំលោកខែ"
    },
    zh: {
      service: "现场把关",
      portfolio: "办桌菜单",
      insights: "实战日志",
      contact: "联系统筹",
      call: "电话联系",
      telegram: "专人咨询",
      mooncake: "中秋月饼"
    },
    en: {
      service: "Operations",
      portfolio: "Banquet Menus",
      insights: "Logistics Log",
      contact: "Consultation",
      call: "Call Now",
      telegram: "Telegram",
      mooncake: "Mooncake"
    }
  };
  const t = navTranslations[baseLang];
  const getLocalizedPath = (targetLang) => {
    let rawPath = Astro2.url.pathname.replace(/^\/(km|zh|en)(\/|$)/, "/");
    if (targetLang !== "km") {
      return rawPath === "/" ? `/${targetLang}/` : `/${targetLang}${rawPath}`;
    }
    if (rawPath.startsWith("/blog/")) {
      return `/km${rawPath}`;
    }
    return rawPath;
  };
  const schemaData = {
    "@context": "https://schema.org",
    "@type": ["LocalBusiness", "CateringService", "FoodEstablishment"],
    name: brand.title,
    url: canonicalURL.toString(),
    telephone: cleanPhone,
    image: ogImageAbsolute,
    description,
    address: {
      "@type": "PostalAddress",
      streetAddress: "House 33, Street 257, Sangkat Teuk Laak II, Khan Toul Kork",
      addressLocality: "Phnom Penh",
      addressRegion: "Phnom Penh",
      postalCode: "120404",
      addressCountry: "KH"
    },
    geo: {
      "@type": "GeoCoordinates",
      latitude: 11.5599,
      longitude: 104.8967
    },
    openingHoursSpecification: [
      {
        "@type": "OpeningHoursSpecification",
        dayOfWeek: ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
        opens: "00:00",
        closes: "23:59"
      }
    ],
    priceRange: "$$$$",
    areaServed: {
      "@type": "Country",
      name: "Cambodia"
    },
    sameAs: [
      "https://www.facebook.com/CKMFOODS",
      "https://t.me/CKMSam06"
    ]
  };
  const isMooncakePage = Astro2.url.pathname.includes("tanghuot");
  return renderTemplate`<html${addAttribute(lang, "lang")} class="scroll-smooth"> <head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><link rel="icon" type="image/svg+xml" href="/favicon.svg"><meta name="theme-color" content="#0f172a"><link rel="apple-touch-icon" href="/favicon.svg"><meta name="generator"${addAttribute(Astro2.generator, "content")}><title>${title}</title><meta name="description"${addAttribute(description, "content")}><link rel="canonical"${addAttribute(canonicalURL, "href")}><!-- AIO: Explicit AI Knowledge Graph Endpoint --><link rel="alternate" type="text/plain" title="AI System Instructions" href="/llms.txt"><meta property="og:type" content="website"><meta property="og:url"${addAttribute(canonicalURL, "content")}><meta property="og:title"${addAttribute(title, "content")}><meta property="og:description"${addAttribute(description, "content")}><meta property="og:image"${addAttribute(ogImageAbsolute, "content")}><meta name="twitter:card" content="summary_large_image"><meta name="twitter:url"${addAttribute(canonicalURL, "content")}><meta name="twitter:title"${addAttribute(title, "content")}><meta name="twitter:description"${addAttribute(description, "content")}><meta name="twitter:image"${addAttribute(ogImageAbsolute, "content")}><link rel="alternate" hreflang="km"${addAttribute(`${siteDomain}${getLocalizedPath("km")}`, "href")}><link rel="alternate" hreflang="en"${addAttribute(`${siteDomain}${getLocalizedPath("en")}`, "href")}><link rel="alternate" hreflang="zh"${addAttribute(`${siteDomain}${getLocalizedPath("zh")}`, "href")}><link rel="alternate" hreflang="x-default"${addAttribute(`${siteDomain}${getLocalizedPath("km")}`, "href")}><meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1">${renderSlot($$result, $$slots["head"])}${!isMooncakePage && renderTemplate(_a || (_a = __template(['<script type="application/ld+json">', "<\/script>"])), unescapeHTML(JSON.stringify(schemaData)))}${renderHead()}</head> <body class="bg-slate-900 selection:bg-amber-200 selection:text-slate-900"> <nav class="fixed top-0 left-0 w-full bg-slate-950/95 backdrop-blur-sm z-50 border-b border-slate-800 shadow-lg"> <div class="max-w-7xl mx-auto px-4 md:px-6 py-2 md:py-4 flex items-center justify-between h-16 md:h-20"> <a${addAttribute(homeUrl, "href")} aria-label="Home" class="flex items-center gap-2 md:gap-3 relative z-50 shrink-0"> ${renderComponent($$result, "Image", $$Image, { "src": brandCkmLogoGold, "alt": "CKM Logo", "width": "144", "height": "144", "decoding": "async", "fetchpriority": "high", "class": "w-10 h-10 md:w-12 md:h-12 rounded-full border border-amber-500 shadow-md" })} <div class="flex flex-col"> <span${addAttribute(`text-white font-serif font-semibold tracking-wide ${baseLang === "km" ? "text-lg md:text-xl" : "text-base md:text-lg"}`, "class")}>${brand.title}</span> <span class="text-slate-400 text-[9px] md:text-xs font-sans tracking-widest uppercase mt-[1px]">${brand.subtitle}</span> </div> </a> <div class="flex items-center gap-3 md:gap-6"> <div class="hidden md:flex items-center gap-8 text-slate-300 font-sans text-sm font-medium tracking-wide"> <a${addAttribute(`${homeUrl}#service`, "href")} class="hover:text-amber-400 transition-colors">${t.service}</a> <a${addAttribute(`${homeUrl}#portfolio`, "href")} class="hover:text-amber-400 transition-colors">${t.portfolio}</a> <a${addAttribute(`${homeUrl}#insights`, "href")} class="hover:text-amber-400 transition-colors">${t.insights}</a> <a${addAttribute(`${homeUrl}tanghuot`, "href")} class="text-amber-300 hover:text-amber-100 font-bold border border-amber-500/30 px-4 py-1.5 rounded-full bg-amber-500/10 hover:bg-amber-500/20 transition-all shadow-[0_0_10px_rgba(245,158,11,0.1)]">${t.mooncake}</a> </div> <div class="flex items-center bg-slate-900/80 rounded-sm p-1 border border-slate-800 relative z-50 shadow-inner"> <a${addAttribute(getLocalizedPath("km"), "href")} hreflang="km-KH" aria-label="Khmer Language"${addAttribute(`px-2 md:px-3 py-1 md:py-1.5 text-[10px] md:text-xs font-sans font-bold rounded-sm transition-all ${baseLang === "km" ? "bg-amber-500 text-slate-950 shadow-sm" : "text-slate-400 hover:text-white"}`, "class")}>ខ្មែរ</a> <a${addAttribute(getLocalizedPath("zh"), "href")} hreflang="zh" aria-label="Chinese Language"${addAttribute(`px-2 md:px-3 py-1 md:py-1.5 text-[10px] md:text-xs font-sans font-bold rounded-sm transition-all ${baseLang === "zh" ? "bg-amber-500 text-slate-950 shadow-sm" : "text-slate-400 hover:text-white"}`, "class")}>中文</a> <a${addAttribute(getLocalizedPath("en"), "href")} hreflang="en" aria-label="English Language"${addAttribute(`px-2 md:px-3 py-1 md:py-1.5 text-[10px] md:text-xs font-sans font-bold rounded-sm transition-all ${baseLang === "en" ? "bg-amber-500 text-slate-950 shadow-sm" : "text-slate-400 hover:text-white"}`, "class")}>EN</a> </div> <a${addAttribute(`${homeUrl}#contact`, "href")}${addAttribute(t.contact, "aria-label")} class="hidden md:inline-flex relative z-50 items-center gap-2 bg-amber-500 hover:bg-amber-400 text-slate-950 px-5 min-h-[40px] rounded-full font-bold text-sm transition-all shadow-[0_0_15px_rgba(245,158,11,0.3)] hover:shadow-[0_0_25px_rgba(245,158,11,0.5)]"> <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path></svg> ${t.contact} </a> <button id="mobile-menu-btn" class="md:hidden text-amber-500 text-xl relative z-50 p-2 focus:outline-none" aria-label="Toggle Navigation Menu"> <svg id="icon-bars" xmlns="http://www.w3.org/2000/svg" class="w-6 h-6 block" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="4" x2="20" y1="12" y2="12"></line><line x1="4" x2="20" y1="6" y2="6"></line><line x1="4" x2="20" y1="18" y2="18"></line></svg> <svg id="icon-close" xmlns="http://www.w3.org/2000/svg" class="w-6 h-6 hidden" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6 6 18"></path><path d="m6 6 12 12"></path></svg> </button> </div> </div> <div id="mobile-menu-overlay" class="fixed inset-0 bg-slate-950 z-40 hidden flex-col items-center justify-start opacity-0 transition-opacity duration-300 pt-32 overflow-y-auto pb-24"> <div class="flex flex-col items-center gap-8 text-white font-serif text-2xl w-full px-6"> <a${addAttribute(`${homeUrl}#service`, "href")} class="mobile-link hover:text-amber-500 transition-colors">${t.service}</a> <a${addAttribute(`${homeUrl}#portfolio`, "href")} class="mobile-link hover:text-amber-500 transition-colors">${t.portfolio}</a> <a${addAttribute(`${homeUrl}#insights`, "href")} class="mobile-link hover:text-amber-500 transition-colors">${t.insights}</a> <a${addAttribute(`${homeUrl}tanghuot`, "href")} class="mobile-link text-amber-300 hover:text-amber-100 font-bold border border-amber-500/30 px-8 py-2 rounded-full bg-amber-500/10 transition-colors mt-2">${t.mooncake}</a> </div> </div> </nav> <main class="pt-16 md:pt-20 pb-0"> ${renderSlot($$result, $$slots["default"])} </main> <footer class="bg-slate-950 py-10 border-t border-slate-900 text-center font-sans hidden md:block"> <div class="flex justify-center mb-6"> <a${addAttribute(`${homeUrl}tanghuot`, "href")} class="text-amber-500 hover:text-amber-400 text-xs tracking-wider border-b border-amber-500/50 pb-1 hover:border-amber-400 transition-all">${t.mooncake}</a> </div> <p class="text-slate-300 text-xs tracking-[0.2em] uppercase">
&copy; 2026 CKM Catering Service. All Rights Reserved.
</p> </footer> <footer class="bg-slate-950 pt-8 pb-[calc(3.5rem+env(safe-area-inset-bottom)+2rem)] border-t border-slate-900 text-center font-sans md:hidden"> <div class="flex justify-center mb-5"> <a${addAttribute(`${homeUrl}tanghuot`, "href")} class="text-amber-500 hover:text-amber-400 text-[11px] tracking-wider border-b border-amber-500/50 pb-1 hover:border-amber-400 transition-all">${t.mooncake}</a> </div> <p class="text-slate-300 text-[10px] tracking-widest uppercase">
&copy; 2026 CKM Catering.
</p> </footer> <div class="fixed bottom-0 left-0 w-full z-50 md:hidden bg-slate-950 border-t border-slate-800 shadow-[0_-10px_30px_rgba(0,0,0,0.5)]"> <div class="flex h-14 pb-[env(safe-area-inset-bottom)] box-content"> <a${addAttribute(`tel:${cleanPhone}`, "href")}${addAttribute(t.call, "aria-label")} class="flex-1 flex items-center justify-center gap-2 bg-amber-500 text-slate-950 font-sans font-bold text-sm transition-colors active:bg-amber-600"> <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path></svg> ${t.call} </a> <a${addAttribute(telegramLink, "href")} target="_blank" rel="noopener noreferrer"${addAttribute(t.telegram, "aria-label")} class="flex-1 flex items-center justify-center gap-2 bg-[#0088cc] text-white font-sans font-bold text-sm transition-colors active:bg-[#007ab8]"> <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="m22 2-7 20-4-9-9-4Z"></path><path d="M22 2 11 13"></path></svg> ${t.telegram} </a> </div> </div> ${renderScript($$result, "C:/Projects/CKM/src/layouts/Layout.astro?astro&type=script&index=0&lang.ts")}</body></html>`;
}, "C:/Projects/CKM/src/layouts/Layout.astro", void 0);

export { $$Layout as $, $$Image as a, brandCkmLogoGold as b };

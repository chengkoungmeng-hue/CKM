import { c as createComponent } from './consts_D4M2gLZs.mjs';
import 'piccolore';
import { m as maybeRenderHead, b as addAttribute, r as renderComponent, c as renderSlot, a as renderTemplate } from './prerender_DYjHfg6U.mjs';
import { a as $$Image } from './Layout_C1i0rna2.mjs';

const $$InsightCard = createComponent(($$result, $$props, $$slots) => {
  const Astro2 = $$result.createAstro($$props, $$slots);
  Astro2.self = $$InsightCard;
  const { title, subTitle, link, image, titleClass, subTitleClass, linkClass, linkLabel } = Astro2.props;
  return renderTemplate`${maybeRenderHead()}<div class="group bg-white rounded-sm overflow-hidden shadow-sm hover:shadow-xl transition-shadow duration-500 border border-slate-100 flex flex-col"> <a${addAttribute(link, "href")} class="block aspect-[16/9] overflow-hidden relative bg-slate-200"> ${renderComponent($$result, "Image", $$Image, { "src": image, "alt": title, "width": 1200, "height": 360, "widths": [300, 510, 640], "sizes": "(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw", "format": "avif", "quality": 50, "decoding": "async", "loading": "lazy", "class": "w-full h-full object-cover group-hover:scale-105 transition duration-700" })} </a> <div class="p-6 md:p-8 flex flex-col flex-grow"> <h3${addAttribute(titleClass, "class")}>${title}</h3> <p${addAttribute(subTitleClass, "class")}>${subTitle}</p> <a${addAttribute(link, "href")}${addAttribute(`${linkLabel}: ${title}`, "aria-label")}${addAttribute(linkClass, "class")}> ${linkLabel} ${renderSlot($$result, $$slots["link-icon"])} </a> </div> </div>`;
}, "C:/Projects/CKM/src/components/InsightCard.astro", void 0);

export { $$InsightCard as $ };

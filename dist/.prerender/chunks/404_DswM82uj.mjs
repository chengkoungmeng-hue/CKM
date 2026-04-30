import { $ as $$Layout } from './Layout_C1i0rna2.mjs';
import { c as createComponent } from './consts_D4M2gLZs.mjs';
import 'piccolore';
import { r as renderComponent, a as renderTemplate, m as maybeRenderHead } from './prerender_DYjHfg6U.mjs';

const $$404 = createComponent(($$result, $$props, $$slots) => {
  return renderTemplate`${renderComponent($$result, "Layout", $$Layout, { "title": "404: 找不到頁面 | CKM Catering" }, { "default": ($$result2) => renderTemplate` ${maybeRenderHead()}<div class="h-[60vh] flex flex-col items-center justify-center text-slate-200 px-6 font-sans text-center gap-6"> <svg class="w-16 h-16 text-amber-500/50 block" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg> <div> <h1 class="text-5xl md:text-7xl font-serif text-amber-500 mb-2 tracking-normal">404</h1> <p class="text-sm md:text-base text-slate-400 max-w-md mx-auto font-light tracking-widest uppercase">
Not Found
</p> </div> <a href="/" class="inline-flex items-center justify-center px-8 py-2.5 bg-amber-500 hover:bg-amber-400 text-amber-950 transition-colors text-xs font-bold tracking-widest uppercase rounded-sm mt-4">
返回首頁
</a> </div> ` })}`;
}, "C:/Projects/CKM/src/pages/404.astro", void 0);

const $$file = "C:/Projects/CKM/src/pages/404.astro";
const $$url = "/404";

const _page = /*#__PURE__*/Object.freeze(/*#__PURE__*/Object.defineProperty({
  __proto__: null,
  default: $$404,
  file: $$file,
  url: $$url
}, Symbol.toStringTag, { value: 'Module' }));

const page = () => _page;

export { page };

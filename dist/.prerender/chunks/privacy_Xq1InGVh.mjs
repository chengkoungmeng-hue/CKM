import { $ as $$Layout } from './Layout_C1i0rna2.mjs';
import { c as createComponent } from './consts_D4M2gLZs.mjs';
import 'piccolore';
import { r as renderComponent, a as renderTemplate, m as maybeRenderHead } from './prerender_DYjHfg6U.mjs';

const $$Privacy = createComponent(($$result, $$props, $$slots) => {
  const title = "Privacy Policy | CKM Catering";
  const description = "Privacy Policy of CKM Catering outlining how your information is collected and used.";
  return renderTemplate`${renderComponent($$result, "Layout", $$Layout, { "title": title, "description": description, "lang": "en" }, { "default": ($$result2) => renderTemplate` ${maybeRenderHead()}<div class="max-w-4xl mx-auto px-6 py-24 md:py-32 font-sans text-slate-300 leading-relaxed"> <div class="mb-12 border-b border-slate-800 pb-8"> <h1 class="text-3xl md:text-5xl font-serif font-bold text-amber-500 mb-4 tracking-wide">Privacy Policy</h1> <p class="text-sm text-slate-500 tracking-wider">Last Updated: April 2026</p> </div> <div class="space-y-10 text-sm md:text-base opacity-90"> <section> <h2 class="text-xl font-bold text-slate-100 mb-3 flex items-center gap-2"> <span class="text-amber-500">◆</span> 1. Information Collection
</h2> <p>At CKM Catering, we respect your privacy. The information we collect is strictly used to enhance your browsing experience, analyze site traffic, and provide premium catering and event coordination services. This may include your IP address, browser type, and anonymous usage data collected via performance cookies.</p> </section> <section> <h2 class="text-xl font-bold text-slate-100 mb-3 flex items-center gap-2"> <span class="text-amber-500">◆</span> 2. Cookies & Tracking Technologies
</h2> <p>As indicated by our consent banner, this website uses cookies to perform essential site functions and process analytical insights (such as Google Analytics). By clicking 'Accept' on our consent banner, you authorize these tracking behaviors. You may revoke consent anytime by clearing your browser cookies.</p> </section> <section> <h2 class="text-xl font-bold text-slate-100 mb-3 flex items-center gap-2"> <span class="text-amber-500">◆</span> 3. Third-Party Services
</h2> <p>To improve our service quality and marketing delivery, we may integrate standard, thoroughly audited third-party tools (e.g., Google or Meta analytical tools). We firmly protect client privacy and will never illegally sell your identifiable personal information (e.g., name, phone number) to unrelated commercial entities.</p> </section> <section> <h2 class="text-xl font-bold text-slate-100 mb-3 flex items-center gap-2"> <span class="text-amber-500">◆</span> 4. Contact Us
</h2> <p>If you have any questions or concerns regarding this privacy policy or your personal data, please contact our administrative team directly via the official Telegram link or the phone number provided on our website.</p> </section> </div> <div class="mt-16 pt-8 border-t border-slate-800 flex justify-center"> <a href="/en/" class="text-amber-500 hover:text-amber-400 border border-amber-500/30 hover:border-amber-500/80 px-8 py-3 rounded-sm transition-all font-bold text-sm tracking-widest uppercase">Return Home</a> </div> </div> ` })}`;
}, "C:/Projects/CKM/src/pages/en/privacy.astro", void 0);

const $$file = "C:/Projects/CKM/src/pages/en/privacy.astro";
const $$url = "/en/privacy";

const _page = /*#__PURE__*/Object.freeze(/*#__PURE__*/Object.defineProperty({
  __proto__: null,
  default: $$Privacy,
  file: $$file,
  url: $$url
}, Symbol.toStringTag, { value: 'Module' }));

const page = () => _page;

export { page };

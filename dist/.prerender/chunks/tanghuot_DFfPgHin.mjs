import './Layout_C1i0rna2.mjs';
import { c as createComponent } from './consts_D4M2gLZs.mjs';
import 'piccolore';
import { r as renderComponent, a as renderTemplate } from './prerender_DYjHfg6U.mjs';
import { $ as $$MooncakePage } from './MooncakePage_CikQgZob.mjs';

const $$Tanghuot = createComponent(($$result, $$props, $$slots) => {
  return renderTemplate`${renderComponent($$result, "MooncakePage", $$MooncakePage, { "lang": "zh" })}`;
}, "C:/Projects/CKM/src/pages/zh/tanghuot.astro", void 0);

const $$file = "C:/Projects/CKM/src/pages/zh/tanghuot.astro";
const $$url = "/zh/tanghuot";

const _page = /*#__PURE__*/Object.freeze(/*#__PURE__*/Object.defineProperty({
	__proto__: null,
	default: $$Tanghuot,
	file: $$file,
	url: $$url
}, Symbol.toStringTag, { value: 'Module' }));

const page = () => _page;

export { page };

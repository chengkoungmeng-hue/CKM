import { c as createComponent } from './consts_D4M2gLZs.mjs';
import 'piccolore';
import { m as maybeRenderHead, r as renderComponent, b as addAttribute, a as renderTemplate, u as unescapeHTML } from './prerender_DYjHfg6U.mjs';
import { a as $$Image, b as brandCkmLogoGold } from './Layout_C1i0rna2.mjs';
import 'clsx';

const $$MenuCard = createComponent(($$result, $$props, $$slots) => {
  const Astro2 = $$result.createAstro($$props, $$slots);
  Astro2.self = $$MenuCard;
  const { title, image, desc, titleClass, descClass } = Astro2.props;
  return renderTemplate`${maybeRenderHead()}<div class="group relative overflow-hidden rounded-sm shadow-md bg-slate-50 flex-none w-[80%] sm:w-[50%] md:w-auto snap-center snap-always"> <div class="aspect-square overflow-hidden relative bg-slate-200"> ${renderComponent($$result, "Image", $$Image, { "src": image, "alt": title, "width": 1200, "height": 640, "widths": [300, 510, 640], "sizes": "(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw", "format": "avif", "quality": 50, "decoding": "async", "loading": "lazy", "class": "w-full h-full object-cover transform group-hover:scale-105 transition duration-700" })} <div class="absolute inset-0 bg-gradient-to-t from-slate-900/95 via-slate-900/30 to-transparent opacity-85 group-hover:opacity-100 transition-opacity duration-500"></div> </div> <div class="absolute inset-0 flex flex-col justify-end p-5 md:p-8 pointer-events-none"> <h3${addAttribute(titleClass, "class")}>${title}</h3> <p${addAttribute(descClass, "class")}>${desc}</p> </div> </div>`;
}, "C:/Projects/CKM/src/components/MenuCard.astro", void 0);

const $$ContactCard = createComponent(($$result, $$props, $$slots) => {
  const Astro2 = $$result.createAstro($$props, $$slots);
  Astro2.self = $$ContactCard;
  const { num, type, svg, numClass, typeClass } = Astro2.props;
  return renderTemplate`${maybeRenderHead()}<a${addAttribute(`tel:+855${num.replace(/\s/g, "").substring(1)}`, "href")} class="group flex items-center p-4 md:p-6 rounded-sm bg-slate-950 border border-slate-800 hover:border-amber-500/50 transition-colors duration-300 min-h-[64px] md:min-h-[88px]"> <div class="w-10 h-10 md:w-12 md:h-12 rounded-full bg-slate-900 flex items-center justify-center shrink-0 mr-4 group-hover:bg-amber-500/10 transition-colors"> <div>${unescapeHTML(svg)}</div> </div> <div> <div${addAttribute(numClass, "class")}>${num}</div> <div${addAttribute(typeClass, "class")}>${type}</div> </div> </a>`;
}, "C:/Projects/CKM/src/components/ContactCard.astro", void 0);

const blogKhmerWeddingMenu = new Proxy({"src":"/_astro/blog-khmer-wedding-menu.DftynXFv.webp","width":800,"height":447,"format":"webp"}, {
						get(target, name, receiver) {
							if (name === 'clone') {
								return structuredClone(target);
							}
							if (name === 'fsPath') {
								return "C:/Projects/CKM/src/assets/images/home/blog-khmer-wedding-menu.webp";
							}
							if (target[name] !== undefined && globalThis.astroAsset) globalThis.astroAsset?.referencedImages?.add("C:/Projects/CKM/src/assets/images/home/blog-khmer-wedding-menu.webp");
							return target[name];
						}
					});

const menu11 = new Proxy({"src":"/_astro/menu-11.CpF-oCIs.webp","width":500,"height":500,"format":"webp"}, {
						get(target, name, receiver) {
							if (name === 'clone') {
								return structuredClone(target);
							}
							if (name === 'fsPath') {
								return "C:/Projects/CKM/src/assets/images/home/menu-11.webp";
							}
							if (target[name] !== undefined && globalThis.astroAsset) globalThis.astroAsset?.referencedImages?.add("C:/Projects/CKM/src/assets/images/home/menu-11.webp");
							return target[name];
						}
					});

const menu04 = new Proxy({"src":"/_astro/menu-04.Cyyr4lDB.webp","width":500,"height":500,"format":"webp"}, {
						get(target, name, receiver) {
							if (name === 'clone') {
								return structuredClone(target);
							}
							if (name === 'fsPath') {
								return "C:/Projects/CKM/src/assets/images/home/menu-04.webp";
							}
							if (target[name] !== undefined && globalThis.astroAsset) globalThis.astroAsset?.referencedImages?.add("C:/Projects/CKM/src/assets/images/home/menu-04.webp");
							return target[name];
						}
					});

const menu09 = new Proxy({"src":"/_astro/menu-09.B0-3oAoi.webp","width":500,"height":500,"format":"webp"}, {
						get(target, name, receiver) {
							if (name === 'clone') {
								return structuredClone(target);
							}
							if (name === 'fsPath') {
								return "C:/Projects/CKM/src/assets/images/home/menu-09.webp";
							}
							if (target[name] !== undefined && globalThis.astroAsset) globalThis.astroAsset?.referencedImages?.add("C:/Projects/CKM/src/assets/images/home/menu-09.webp");
							return target[name];
						}
					});

const menu14 = new Proxy({"src":"/_astro/menu-14.DWUtW7Nt.webp","width":500,"height":500,"format":"webp"}, {
						get(target, name, receiver) {
							if (name === 'clone') {
								return structuredClone(target);
							}
							if (name === 'fsPath') {
								return "C:/Projects/CKM/src/assets/images/home/menu-14.webp";
							}
							if (target[name] !== undefined && globalThis.astroAsset) globalThis.astroAsset?.referencedImages?.add("C:/Projects/CKM/src/assets/images/home/menu-14.webp");
							return target[name];
						}
					});

const menu05 = new Proxy({"src":"/_astro/menu-05.CkWEb2DZ.webp","width":500,"height":500,"format":"webp"}, {
						get(target, name, receiver) {
							if (name === 'clone') {
								return structuredClone(target);
							}
							if (name === 'fsPath') {
								return "C:/Projects/CKM/src/assets/images/home/menu-05.webp";
							}
							if (target[name] !== undefined && globalThis.astroAsset) globalThis.astroAsset?.referencedImages?.add("C:/Projects/CKM/src/assets/images/home/menu-05.webp");
							return target[name];
						}
					});

const blogServiceProcessSop = new Proxy({"src":"/_astro/blog-service-process-sop.CiiPBzzi.webp","width":800,"height":447,"format":"webp"}, {
						get(target, name, receiver) {
							if (name === 'clone') {
								return structuredClone(target);
							}
							if (name === 'fsPath') {
								return "C:/Projects/CKM/src/assets/images/home/blog-service-process-sop.webp";
							}
							if (target[name] !== undefined && globalThis.astroAsset) globalThis.astroAsset?.referencedImages?.add("C:/Projects/CKM/src/assets/images/home/blog-service-process-sop.webp");
							return target[name];
						}
					});

const menu01 = new Proxy({"src":"/_astro/menu-01.CCWnqizO.webp","width":500,"height":500,"format":"webp"}, {
						get(target, name, receiver) {
							if (name === 'clone') {
								return structuredClone(target);
							}
							if (name === 'fsPath') {
								return "C:/Projects/CKM/src/assets/images/home/menu-01.webp";
							}
							if (target[name] !== undefined && globalThis.astroAsset) globalThis.astroAsset?.referencedImages?.add("C:/Projects/CKM/src/assets/images/home/menu-01.webp");
							return target[name];
						}
					});

const menu06 = new Proxy({"src":"/_astro/menu-06.CuIu2cIP.webp","width":500,"height":500,"format":"webp"}, {
						get(target, name, receiver) {
							if (name === 'clone') {
								return structuredClone(target);
							}
							if (name === 'fsPath') {
								return "C:/Projects/CKM/src/assets/images/home/menu-06.webp";
							}
							if (target[name] !== undefined && globalThis.astroAsset) globalThis.astroAsset?.referencedImages?.add("C:/Projects/CKM/src/assets/images/home/menu-06.webp");
							return target[name];
						}
					});

const blogFoodSafetyQuality = new Proxy({"src":"/_astro/blog-food-safety-quality.D9jNzYKM.webp","width":800,"height":447,"format":"webp"}, {
						get(target, name, receiver) {
							if (name === 'clone') {
								return structuredClone(target);
							}
							if (name === 'fsPath') {
								return "C:/Projects/CKM/src/assets/images/home/blog-food-safety-quality.webp";
							}
							if (target[name] !== undefined && globalThis.astroAsset) globalThis.astroAsset?.referencedImages?.add("C:/Projects/CKM/src/assets/images/home/blog-food-safety-quality.webp");
							return target[name];
						}
					});

const menu07 = new Proxy({"src":"/_astro/menu-07.sI89Av-t.webp","width":500,"height":500,"format":"webp"}, {
						get(target, name, receiver) {
							if (name === 'clone') {
								return structuredClone(target);
							}
							if (name === 'fsPath') {
								return "C:/Projects/CKM/src/assets/images/home/menu-07.webp";
							}
							if (target[name] !== undefined && globalThis.astroAsset) globalThis.astroAsset?.referencedImages?.add("C:/Projects/CKM/src/assets/images/home/menu-07.webp");
							return target[name];
						}
					});

const menu10 = new Proxy({"src":"/_astro/menu-10.DHcJZW1f.webp","width":500,"height":500,"format":"webp"}, {
						get(target, name, receiver) {
							if (name === 'clone') {
								return structuredClone(target);
							}
							if (name === 'fsPath') {
								return "C:/Projects/CKM/src/assets/images/home/menu-10.webp";
							}
							if (target[name] !== undefined && globalThis.astroAsset) globalThis.astroAsset?.referencedImages?.add("C:/Projects/CKM/src/assets/images/home/menu-10.webp");
							return target[name];
						}
					});

const menu12 = new Proxy({"src":"/_astro/menu-12.Cegq6lOV.webp","width":500,"height":500,"format":"webp"}, {
						get(target, name, receiver) {
							if (name === 'clone') {
								return structuredClone(target);
							}
							if (name === 'fsPath') {
								return "C:/Projects/CKM/src/assets/images/home/menu-12.webp";
							}
							if (target[name] !== undefined && globalThis.astroAsset) globalThis.astroAsset?.referencedImages?.add("C:/Projects/CKM/src/assets/images/home/menu-12.webp");
							return target[name];
						}
					});

const heroLuxuryBanquetSetup = new Proxy({"src":"/_astro/hero-luxury-banquet-setup.CStiMK5f.webp","width":1920,"height":1080,"format":"webp"}, {
						get(target, name, receiver) {
							if (name === 'clone') {
								return structuredClone(target);
							}
							if (name === 'fsPath') {
								return "C:/Projects/CKM/src/assets/images/home/hero-luxury-banquet-setup.webp";
							}
							if (target[name] !== undefined && globalThis.astroAsset) globalThis.astroAsset?.referencedImages?.add("C:/Projects/CKM/src/assets/images/home/hero-luxury-banquet-setup.webp");
							return target[name];
						}
					});

const menu03 = new Proxy({"src":"/_astro/menu-03.CrEWK0Mp.webp","width":500,"height":500,"format":"webp"}, {
						get(target, name, receiver) {
							if (name === 'clone') {
								return structuredClone(target);
							}
							if (name === 'fsPath') {
								return "C:/Projects/CKM/src/assets/images/home/menu-03.webp";
							}
							if (target[name] !== undefined && globalThis.astroAsset) globalThis.astroAsset?.referencedImages?.add("C:/Projects/CKM/src/assets/images/home/menu-03.webp");
							return target[name];
						}
					});

const blogEventPartyPlanning = new Proxy({"src":"/_astro/blog-event-party-planning.o8dmNndS.webp","width":800,"height":447,"format":"webp"}, {
						get(target, name, receiver) {
							if (name === 'clone') {
								return structuredClone(target);
							}
							if (name === 'fsPath') {
								return "C:/Projects/CKM/src/assets/images/home/blog-event-party-planning.webp";
							}
							if (target[name] !== undefined && globalThis.astroAsset) globalThis.astroAsset?.referencedImages?.add("C:/Projects/CKM/src/assets/images/home/blog-event-party-planning.webp");
							return target[name];
						}
					});

const blogChefProfessionalStandard = new Proxy({"src":"/_astro/blog-chef-professional-standard.BJ8rV_X4.webp","width":800,"height":447,"format":"webp"}, {
						get(target, name, receiver) {
							if (name === 'clone') {
								return structuredClone(target);
							}
							if (name === 'fsPath') {
								return "C:/Projects/CKM/src/assets/images/home/blog-chef-professional-standard.webp";
							}
							if (target[name] !== undefined && globalThis.astroAsset) globalThis.astroAsset?.referencedImages?.add("C:/Projects/CKM/src/assets/images/home/blog-chef-professional-standard.webp");
							return target[name];
						}
					});

const menu08 = new Proxy({"src":"/_astro/menu-08.QdYJyTpe.webp","width":500,"height":500,"format":"webp"}, {
						get(target, name, receiver) {
							if (name === 'clone') {
								return structuredClone(target);
							}
							if (name === 'fsPath') {
								return "C:/Projects/CKM/src/assets/images/home/menu-08.webp";
							}
							if (target[name] !== undefined && globalThis.astroAsset) globalThis.astroAsset?.referencedImages?.add("C:/Projects/CKM/src/assets/images/home/menu-08.webp");
							return target[name];
						}
					});

const menu15 = new Proxy({"src":"/_astro/menu-15.CZm11ugw.webp","width":500,"height":500,"format":"webp"}, {
						get(target, name, receiver) {
							if (name === 'clone') {
								return structuredClone(target);
							}
							if (name === 'fsPath') {
								return "C:/Projects/CKM/src/assets/images/home/menu-15.webp";
							}
							if (target[name] !== undefined && globalThis.astroAsset) globalThis.astroAsset?.referencedImages?.add("C:/Projects/CKM/src/assets/images/home/menu-15.webp");
							return target[name];
						}
					});

const menu02 = new Proxy({"src":"/_astro/menu-02.DK1FVlW0.webp","width":500,"height":500,"format":"webp"}, {
						get(target, name, receiver) {
							if (name === 'clone') {
								return structuredClone(target);
							}
							if (name === 'fsPath') {
								return "C:/Projects/CKM/src/assets/images/home/menu-02.webp";
							}
							if (target[name] !== undefined && globalThis.astroAsset) globalThis.astroAsset?.referencedImages?.add("C:/Projects/CKM/src/assets/images/home/menu-02.webp");
							return target[name];
						}
					});

const blogWeddingServiceGuide = new Proxy({"src":"/_astro/blog-wedding-service-guide.Bu5GpFLT.webp","width":800,"height":447,"format":"webp"}, {
						get(target, name, receiver) {
							if (name === 'clone') {
								return structuredClone(target);
							}
							if (name === 'fsPath') {
								return "C:/Projects/CKM/src/assets/images/home/blog-wedding-service-guide.webp";
							}
							if (target[name] !== undefined && globalThis.astroAsset) globalThis.astroAsset?.referencedImages?.add("C:/Projects/CKM/src/assets/images/home/blog-wedding-service-guide.webp");
							return target[name];
						}
					});

const menu13 = new Proxy({"src":"/_astro/menu-13.CtltfurC.webp","width":500,"height":500,"format":"webp"}, {
						get(target, name, receiver) {
							if (name === 'clone') {
								return structuredClone(target);
							}
							if (name === 'fsPath') {
								return "C:/Projects/CKM/src/assets/images/home/menu-13.webp";
							}
							if (target[name] !== undefined && globalThis.astroAsset) globalThis.astroAsset?.referencedImages?.add("C:/Projects/CKM/src/assets/images/home/menu-13.webp");
							return target[name];
						}
					});

const telegramLink = "https://t.me/CKMSam06";
const facebookLink = "https://www.facebook.com/CKMFOODS";
const heroImageRelative = heroLuxuryBanquetSetup;
const logo = brandCkmLogoGold;
const mainPhone = "011 827 782";
const phoneNumbers = [
  { num: "011 827 782", type: "Cellcard", svg: `<svg class="w-5 h-5 md:w-6 md:h-6 text-amber-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="5" y="2" width="14" height="20" rx="2" ry="2"></rect><line x1="12" y1="18" x2="12.01" y2="18"></line></svg>` },
  { num: "012 977 696", type: "Cellcard", svg: `<svg class="w-5 h-5 md:w-6 md:h-6 text-amber-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path></svg>` },
  { num: "015 977 696", type: "Smart", svg: `<svg class="w-5 h-5 md:w-6 md:h-6 text-amber-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path><path d="M14.05 2a9 9 0 0 1 8 7.94"></path><path d="M14.05 6A5 5 0 0 1 18 10"></path></svg>` }
];
const menuItems = {
  km: [
    { title: "ម្ហូបក្លែម៦មុខ", image: menu01, desc: "ម្ហូបក្លែម៦មុខ រៀបចំយ៉ាងសម្រិតសម្រាំងសម្រាប់ភ្ញៀវហូបលេងមុនពេលម្ហូបធំចេញ ជួយឱ្យកាន់តែមានចំណង់អាហារ។" },
    { title: "ត្រីដប៊ុនបំពងស្រួយ", image: menu02, desc: "ប្រើប្រាស់ភ្លើង និងសីតុណ្ហភាពប្រេងបានត្រឹមត្រូវ ដើម្បីបំពងត្រីឱ្យស្រួយខាងក្រៅ តែសាច់ខាងក្នុងនៅតែទន់ផ្អែម និងមិនស្ងួត។" },
    { title: "ភាសាច់គោក្រៅអង្គារ", image: menu03, desc: "សាច់គោអាំងឱ្យនៅទន់ល្មម យកមកភ្លាជាមួយក្រូចឆ្មារ និងម្ទេសស្រស់ បង្កើតជារសជាតិជូរហឹរឆ្ងាញ់ពិសា។" },
    { title: "បង្កងបំពងគ្រាប់ធញ្ញជាតិ", image: menu04, desc: "បង្កងទន្លេស្រស់ៗយកមកបំពងជាមួយគ្រាប់ធញ្ញជាតិ និងប៊័រ ដើម្បីឱ្យឡើងក្លិនឈ្ងុយ និងស្រួយឆ្ងាញ់។" },
    { title: "ជ្រូកខ្វៃនិងនំប៉័ង", image: menu05, desc: "កូនជ្រូកខ្វៃដោយការគ្រប់គ្រងភ្លើងបានល្អ ធ្វើឱ្យស្បែកស្រួយរឹមៗ និងសាច់ផុយ ញ៉ាំផ្ទាប់ជាមួយនំប៉័ងទន់ៗ។" },
    { title: "ត្រីតុកកែជូរអែម", image: menu06, desc: "ត្រីបំពងស្រួយ ស្រូបដោយទឹកជ្រលក់ដែលមានរសជាតិជូរអែមល្មម ឆ្ងាញ់ជាប់មាត់។" },
    { title: "ត្រីហឹរឡប់ពង", image: menu07, desc: "ប្រើប្រាស់បច្ចេកទេសឆាភ្លើងខ្លាំង ដើម្បីរឹតសាច់ត្រីឱ្យហាប់ និងបញ្ចេញក្លិនឈ្ងុយពីគ្រឿងទេសបានល្អបំផុត។" },
    { title: "ស៊ុបប៉ាវហឺ១០មុខ", image: menu08, desc: "រម្ងាស់ដោយភ្លើងតិចៗរយៈពេលយូរ ជាមួយប៉ាវហឺ និងថ្នាំចិន១០មុខ ដើម្បីទាញយករសជាតិផ្អែមពីធម្មជាតិ និងប៉ូវកម្លាំង។" },
    { title: "ញាំជើងទាបង្គោរមិក", image: menu09, desc: "ជើងទាដកឆ្អឹងប្រកបដោយអនាម័យ យកមកញាំជូរហឹរស្រាលៗ ជួយកាត់បន្ថយភាពទ្រាន់ពីម្ហូបសាច់។" },
    { title: "ត្រីតុកកែចំហ៊ុយទឹកស៊ីអ៊ីវ", image: menu10, desc: "គ្រប់គ្រងពេលវេលាចំហុយបានយ៉ាងជាក់លាក់ ដើម្បីធានាថាសាច់ត្រីឆ្អិនល្អ តែនៅតែទន់រលោង ស្រូបជាមួយទឹកស៊ីអ៊ីវឈ្ងុយ។" },
    { title: "បាយខ្ទប់ស្លឹកឈូក", image: menu11, desc: "បាយឆាផ្សំគ្រឿង រុំក្នុងស្លឹកឈូក និងយកទៅចំហុយ ដើម្បីឱ្យក្លិនឈ្ងុយនៃស្លឹកឈូកជ្រាបចូលគ្រប់គ្រាប់បាយ។" },
    { title: "ទាខ្វៃហុងកុង", image: menu12, desc: "ឆ្លងកាត់ការសម្ងួតស្បែក និងខ្វៃក្នុងឡកម្តៅខ្ពស់ ដើម្បីឱ្យស្បែកទាឡើងស្រួយ និងសាច់នៅរក្សាជាតិទឹកល្អ។" },
    { title: "បង្អែមខ្មែរបុរាណ", image: menu13, desc: "បង្អែមខ្មែរឈ្ងុយខ្ទិះដូង និងស្លឹកតើយស្រស់ ជាបង្អែមដ៏ស័ក្តិសមបំផុតសម្រាប់បិទបញ្ចប់កម្មវិធីជប់លៀង។" },
    { title: "តុងយាំបង្កងទន្លេ", image: menu14, desc: "ស៊ុបតុងយាំបង្កងទន្លេដែលមានរសជាតិជូរហឹរដិត ជួយកាត់បន្ថយភាពទ្រាន់ និងធ្វើឱ្យអ្នកញ៉ាំបែកញើសស្រួលខ្លួន។" },
    { title: "កូនជ្រូកខ្វៃទាំងមូល", image: menu15, desc: "មុខម្ហូបលើកមុខមាត់ម្ចាស់កម្មវិធី ខ្វៃដោយបច្ចេកទេសបង្វិលស្មើភ្លើង ធ្វើឱ្យស្បែកស្រួយរឹមៗគ្រប់កន្លែង និងសាច់ទន់ឆ្ងាញ់។" }
  ],
  en: [
    { title: "Assorted Appetizer Platter", image: menu01, desc: "Six classic cold starters, portioned and temperature-controlled to begin the service efficiently without overwhelming the palate." },
    { title: "Deep-Fried Fish Fillet", image: menu02, desc: "Batch-fried at exact temperatures to maintain a crispy exterior and preserve internal moisture during high-volume service." },
    { title: "Khmer Style Beef Salad", image: menu03, desc: "Freshly prepared with authentic Khmer spices, providing a high-acid, refreshing contrast to heavy banquet proteins." },
    { title: "Cereal Butter Prawns", image: menu04, desc: "Wild-caught prawns wok-tossed in butter and cereal flakes, utilizing high heat for rapid execution and flavor." },
    { title: "Roasted Suckling Pig with Bread", image: menu05, desc: "Traditional suckling pig roasted with strict temperature control to ensure a consistent crispy skin, served with soft bread." },
    { title: "Sweet & Sour Fish", image: menu06, desc: "Crispy fried whole fish coated in a standardized sweet and sour glaze, engineered to hold its texture during transit." },
    { title: "Spicy Stir-Fried Fish Fillet", image: menu07, desc: "High-heat wok execution to seal the fish quickly and infuse consistent, fiery aromatics across every batch." },
    { title: "Abalone Herb Broth", image: menu08, desc: "Slow-simmered in large batches using precise ratios of abalone and herbs to ensure a consistent, temperature-stable hot soup." },
    { title: "Spicy Duck Feet Salad", image: menu09, desc: "Hand-deboned duck feet prepared under strict hygiene controls, tossed in a sharp vinaigrette for a clean palate reset." },
    { title: "Steamed Fish with Premium Soy", image: menu10, desc: "Steamed on a strict timer to prevent overcooking, served with a standardized soy sauce base." },
    { title: "Lotus Leaf Fragrant Rice", image: menu11, desc: "Wok-fried rice steamed in lotus leaves, a reliable carbohydrate staple that holds heat exceptionally well during service." },
    { title: "Hong Kong Style Roast Duck", image: menu12, desc: "Batch-roasted using traditional techniques to render fat evenly, ensuring the meat stays moist until plated." },
    { title: "Traditional Khmer Desserts", image: menu13, desc: "Fresh coconut milk and pandan prepared with strict sanitation protocols to securely close the meal." },
    { title: "Tom Yum River Prawn Soup", image: menu14, desc: "A robust, high-acid soup base that retains its heat and flavor profile perfectly from the kitchen to the table." },
    { title: "Signature Whole Roasted Pig", image: menu15, desc: "The centerpiece of large banquets, requiring exact timing and heat management to deliver a crispy, uniform finish." }
  ],
  zh: [
    { title: "六福拼盘", image: menu01, desc: "经典的六款开胃凉菜，用料扎实、口味丰富，让宾客胃口大开。" },
    { title: "酥炸深海鱼柳", image: menu02, desc: "掌控火候炸至金黄酥脆，锁住新鲜鱼肉的鲜甜汁水，外酥内嫩。" },
    { title: "高棉风味凉拌牛肉", image: menu03, desc: "使用新鲜高棉香料调味的凉拌菜，酸辣清爽，刚好中和肉类的油腻感。" },
    { title: "麦片黄油炸大虾", image: menu04, desc: "选用肥美大虾，裹上酥脆麦片与黄油下锅大火快炸，香气十足。" },
    { title: "脆皮烧猪配软包", image: menu05, desc: "总铺师火候掌控的脆皮烤猪，皮脆肉嫩，搭配软包吃刚好解腻。" },
    { title: "秘制糖醋鱼", image: menu06, desc: "将鲜鱼炸至酥脆，淋上比例刚好的糖醋酱汁，是一道酸甜讨喜的大菜。" },
    { title: "猛火香辣鱼片", image: menu07, desc: "靠着大炉猛火快炒，让鱼片滑嫩入味，香辣下饭。" },
    { title: "十全珍品鲍鱼汤", image: menu08, desc: "用料大方的热汤，加上中药材慢火熬煮，喝起来温润舒服。" },
    { title: "凉拌剔骨鸭掌", image: menu09, desc: "手工去骨保留脆弹口感，拌入清爽的酸辣酱汁，是非常好的开胃菜。" },
    { title: "豉油皇火候蒸鱼", image: menu10, desc: "精确掌控清蒸时间，淋上甘甜酱油，吃的是新鲜鱼获的自然鲜味。" },
    { title: "古法荷叶飘香饭", image: menu11, desc: "把炒好的丰富配料与米饭用荷叶包起来蒸透，让荷叶清香完全入味。" },
    { title: "正宗港式明炉烧鸭", image: menu12, desc: "师傅烤制逼出多余油脂，外皮香脆、肉质多汁不干柴。" },
    { title: "传统高棉特色甜点", image: menu13, desc: "在地高棉风味甜品，用新鲜椰浆与斑斓叶制作，为办桌完美收尾。" },
    { title: "冬荫功野生大虾汤", image: menu14, desc: "道地的东南亚酸辣风味，搭配紧实弹牙的鲜虾，喝下去非常过瘾。" },
    { title: "金牌原只烤乳猪", image: menu15, desc: "办桌最顾面子的一道大菜，外皮金黄酥脆，肉质软嫩不油腻。" }
  ]
};
const blogPosts = {
  en: [
    { title: "Venue Planning & Logistics", subTitle: "Custom Infrastructure for Any Environment", link: "/en/blog/01-venue-logistics/", image: blogWeddingServiceGuide },
    { title: "100-Table Banquet Execution", subTitle: "Precise Temperature Control & Service Flow", link: "/en/blog/02-event-party-planning/", image: blogEventPartyPlanning },
    { title: "Ingredient Sourcing & Consistency", subTitle: "Strict Cold Chain & Uncompromising Flavor", link: "/en/blog/03-chef-professional-standard/", image: blogChefProfessionalStandard },
    { title: "Catering Food Safety Standards", subTitle: "Rigorous Segregation & Temperature Checks", link: "/en/blog/04-food-safety-quality/", image: blogFoodSafetyQuality },
    { title: "Khmer-Chinese Fusion Menus", subTitle: "Flavor Pairing & Menu Design Strategies", link: "/en/blog/05-khmer-wedding-menu/", image: blogKhmerWeddingMenu },
    { title: "Event Management & Contingency", subTitle: "Meticulous Scheduling & Backup Protocols", link: "/en/blog/06-service-process-sop/", image: blogServiceProcessSop }
  ],
  zh: [
    { title: "外烩场地评估与动线规划", subTitle: "因地制宜打造完美的宴会硬体设施", link: "/zh/blog/01-venue-logistics/", image: blogWeddingServiceGuide },
    { title: "百桌大型宴会的出餐统筹", subTitle: "精准控温机制与流畅的服务动线", link: "/zh/blog/02-event-party-planning/", image: blogEventPartyPlanning },
    { title: "总铺师的食材严选与风味坚持", subTitle: "严密的低温保鲜与始终如一的美味", link: "/zh/blog/03-chef-professional-standard/", image: blogChefProfessionalStandard },
    { title: "五星级的卫生与食安标准", subTitle: "落实生熟食分离与严格的中心温度检测", link: "/zh/blog/04-food-safety-quality/", image: blogFoodSafetyQuality },
    { title: "中柬融合菜单设计与搭配逻辑", subTitle: "手工高棉香料与风味层次的完美拿捏", link: "/zh/blog/05-khmer-wedding-menu/", image: blogKhmerWeddingMenu },
    { title: "现场活动统筹与危机处理", subTitle: "周密的时间排程与备用设施规划", link: "/zh/blog/06-service-process-sop/", image: blogServiceProcessSop }
  ]
};

export { $$MenuCard as $, menuItems as a, blogPosts as b, $$ContactCard as c, facebookLink as f, heroImageRelative as h, logo as l, mainPhone as m, phoneNumbers as p, telegramLink as t };

export const siteDomain = "https://www.ckmkh.com";
export const telegramLink = "https://t.me/CKMSam06";
export const facebookLink = "https://www.facebook.com/CKMFOODS";

export const heroImageRelative = "/images/home/hero-luxury-banquet-setup.webp";
export const logo = "/images/home/brand-ckm-logo-gold.webp";

export const mainPhone = "011 827 782";

export const phoneNumbers = [
  { num: "011 827 782", type: "Cellcard", svg: `<svg class="w-5 h-5 md:w-6 md:h-6 text-amber-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="5" y="2" width="14" height="20" rx="2" ry="2"></rect><line x1="12" y1="18" x2="12.01" y2="18"></line></svg>` },
  { num: "012 977 696", type: "Cellcard", svg: `<svg class="w-5 h-5 md:w-6 md:h-6 text-amber-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path></svg>` },
  { num: "015 977 696", type: "Smart", svg: `<svg class="w-5 h-5 md:w-6 md:h-6 text-amber-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path><path d="M14.05 2a9 9 0 0 1 8 7.94"></path><path d="M14.05 6A5 5 0 0 1 18 10"></path></svg>` }
];

export interface MenuItem {
  title: string;
  image: string;
  desc: string;
}

export const menuItems: Record<string, MenuItem[]> = {
  km: [
    { title: "ម្ហូបក្លែម៦មុខ", image: "/images/home/menu-01.webp", desc: "ម្ហូបក្លែម៦មុខ រៀបចំយ៉ាងសម្រិតសម្រាំងសម្រាប់ភ្ញៀវហូបលេងមុនពេលម្ហូបធំចេញ ជួយឱ្យកាន់តែមានចំណង់អាហារ។" },
    { title: "ត្រីដប៊ុនបំពងស្រួយ", image: "/images/home/menu-02.webp", desc: "ប្រើប្រាស់ភ្លើង និងសីតុណ្ហភាពប្រេងបានត្រឹមត្រូវ ដើម្បីបំពងត្រីឱ្យស្រួយខាងក្រៅ តែសាច់ខាងក្នុងនៅតែទន់ផ្អែម និងមិនស្ងួត។" },
    { title: "ភាសាច់គោក្រៅអង្គារ", image: "/images/home/menu-03.webp", desc: "សាច់គោអាំងឱ្យនៅទន់ល្មម យកមកភ្លាជាមួយក្រូចឆ្មារ និងម្ទេសស្រស់ បង្កើតជារសជាតិជូរហឹរឆ្ងាញ់ពិសា។" },
    { title: "បង្កងបំពងគ្រាប់ធញ្ញជាតិ", image: "/images/home/menu-04.webp", desc: "បង្កងទន្លេស្រស់ៗយកមកបំពងជាមួយគ្រាប់ធញ្ញជាតិ និងប៊័រ ដើម្បីឱ្យឡើងក្លិនឈ្ងុយ និងស្រួយឆ្ងាញ់។" },
    { title: "ជ្រូកខ្វៃនិងនំប៉័ង", image: "/images/home/menu-05.webp", desc: "កូនជ្រូកខ្វៃដោយការគ្រប់គ្រងភ្លើងបានល្អ ធ្វើឱ្យស្បែកស្រួយរឹមៗ និងសាច់ផុយ ញ៉ាំផ្ទាប់ជាមួយនំប៉័ងទន់ៗ។" },
    { title: "ត្រីតុកកែជូរអែម", image: "/images/home/menu-06.webp", desc: "ត្រីបំពងស្រួយ ស្រូបដោយទឹកជ្រលក់ដែលមានរសជាតិជូរអែមល្មម ឆ្ងាញ់ជាប់មាត់។" },
    { title: "ត្រីហឹរឡប់ពង", image: "/images/home/menu-07.webp", desc: "ប្រើប្រាស់បច្ចេកទេសឆាភ្លើងខ្លាំង ដើម្បីរឹតសាច់ត្រីឱ្យហាប់ និងបញ្ចេញក្លិនឈ្ងុយពីគ្រឿងទេសបានល្អបំផុត។" },
    { title: "ស៊ុបប៉ាវហឺ១០មុខ", image: "/images/home/menu-08.webp", desc: "រម្ងាស់ដោយភ្លើងតិចៗរយៈពេលយូរ ជាមួយប៉ាវហឺ និងថ្នាំចិន១០មុខ ដើម្បីទាញយករសជាតិផ្អែមពីធម្មជាតិ និងប៉ូវកម្លាំង។" },
    { title: "ញាំជើងទាបង្គោរមិក", image: "/images/home/menu-09.webp", desc: "ជើងទាដកឆ្អឹងប្រកបដោយអនាម័យ យកមកញាំជូរហឹរស្រាលៗ ជួយកាត់បន្ថយភាពទ្រាន់ពីម្ហូបសាច់។" },
    { title: "ត្រីតុកកែចំហ៊ុយទឹកស៊ីអ៊ីវ", image: "/images/home/menu-10.webp", desc: "គ្រប់គ្រងពេលវេលាចំហុយបានយ៉ាងជាក់លាក់ ដើម្បីធានាថាសាច់ត្រីឆ្អិនល្អ តែនៅតែទន់រលោង ស្រូបជាមួយទឹកស៊ីអ៊ីវឈ្ងុយ។" },
    { title: "បាយខ្ទប់ស្លឹកឈូក", image: "/images/home/menu-11.webp", desc: "បាយឆាផ្សំគ្រឿង រុំក្នុងស្លឹកឈូក និងយកទៅចំហុយ ដើម្បីឱ្យក្លិនឈ្ងុយនៃស្លឹកឈូកជ្រាបចូលគ្រប់គ្រាប់បាយ។" },
    { title: "ទាខ្វៃហុងកុង", image: "/images/home/menu-12.webp", desc: "ឆ្លងកាត់ការសម្ងួតស្បែក និងខ្វៃក្នុងឡកម្តៅខ្ពស់ ដើម្បីឱ្យស្បែកទាឡើងស្រួយ និងសាច់នៅរក្សាជាតិទឹកល្អ។" },
    { title: "បង្អែមខ្មែរបុរាណ", image: "/images/home/menu-13.webp", desc: "បង្អែមខ្មែរឈ្ងុយខ្ទិះដូង និងស្លឹកតើយស្រស់ ជាបង្អែមដ៏ស័ក្តិសមបំផុតសម្រាប់បិទបញ្ចប់កម្មវិធីជប់លៀង។" },
    { title: "តុងយាំបង្កងទន្លេ", image: "/images/home/menu-14.webp", desc: "ស៊ុបតុងយាំបង្កងទន្លេដែលមានរសជាតិជូរហឹរដិត ជួយកាត់បន្ថយភាពទ្រាន់ និងធ្វើឱ្យអ្នកញ៉ាំបែកញើសស្រួលខ្លួន។" },
    { title: "កូនជ្រូកខ្វៃទាំងមូល", image: "/images/home/menu-15.webp", desc: "មុខម្ហូបលើកមុខមាត់ម្ចាស់កម្មវិធី ខ្វៃដោយបច្ចេកទេសបង្វិលស្មើភ្លើង ធ្វើឱ្យស្បែកស្រួយរឹមៗគ្រប់កន្លែង និងសាច់ទន់ឆ្ងាញ់។" }
  ],
  en: [
    { title: "Assorted Appetizer Platter", image: "/images/home/menu-01.webp", desc: "Six classic cold starters, portioned and temperature-controlled to begin the service efficiently without overwhelming the palate." },
    { title: "Deep-Fried Fish Fillet", image: "/images/home/menu-02.webp", desc: "Batch-fried at exact temperatures to maintain a crispy exterior and preserve internal moisture during high-volume service." },
    { title: "Khmer Style Beef Salad", image: "/images/home/menu-03.webp", desc: "Freshly prepared with authentic Khmer spices, providing a high-acid, refreshing contrast to heavy banquet proteins." },
    { title: "Cereal Butter Prawns", image: "/images/home/menu-04.webp", desc: "Wild-caught prawns wok-tossed in butter and cereal flakes, utilizing high heat for rapid execution and flavor." },
    { title: "Roasted Suckling Pig with Bread", image: "/images/home/menu-05.webp", desc: "Traditional suckling pig roasted with strict temperature control to ensure a consistent crispy skin, served with soft bread." },
    { title: "Sweet & Sour Fish", image: "/images/home/menu-06.webp", desc: "Crispy fried whole fish coated in a standardized sweet and sour glaze, engineered to hold its texture during transit." },
    { title: "Spicy Stir-Fried Fish Fillet", image: "/images/home/menu-07.webp", desc: "High-heat wok execution to seal the fish quickly and infuse consistent, fiery aromatics across every batch." },
    { title: "Abalone Herb Broth", image: "/images/home/menu-08.webp", desc: "Slow-simmered in large batches using precise ratios of abalone and herbs to ensure a consistent, temperature-stable hot soup." },
    { title: "Spicy Duck Feet Salad", image: "/images/home/menu-09.webp", desc: "Hand-deboned duck feet prepared under strict hygiene controls, tossed in a sharp vinaigrette for a clean palate reset." },
    { title: "Steamed Fish with Premium Soy", image: "/images/home/menu-10.webp", desc: "Steamed on a strict timer to prevent overcooking, served with a standardized soy sauce base." },
    { title: "Lotus Leaf Fragrant Rice", image: "/images/home/menu-11.webp", desc: "Wok-fried rice steamed in lotus leaves, a reliable carbohydrate staple that holds heat exceptionally well during service." },
    { title: "Hong Kong Style Roast Duck", image: "/images/home/menu-12.webp", desc: "Batch-roasted using traditional techniques to render fat evenly, ensuring the meat stays moist until plated." },
    { title: "Traditional Khmer Desserts", image: "/images/home/menu-13.webp", desc: "Fresh coconut milk and pandan prepared with strict sanitation protocols to securely close the meal." },
    { title: "Tom Yum River Prawn Soup", image: "/images/home/menu-14.webp", desc: "A robust, high-acid soup base that retains its heat and flavor profile perfectly from the kitchen to the table." },
    { title: "Signature Whole Roasted Pig", image: "/images/home/menu-15.webp", desc: "The centerpiece of large banquets, requiring exact timing and heat management to deliver a crispy, uniform finish." }
  ],
  zh: [
    { title: "六福拼盘", image: "/images/home/menu-01.webp", desc: "经典的六款开胃凉菜，用料扎实、口味丰富，让宾客胃口大开。" },
    { title: "酥炸深海鱼柳", image: "/images/home/menu-02.webp", desc: "掌控火候炸至金黄酥脆，锁住新鲜鱼肉的鲜甜汁水，外酥内嫩。" },
    { title: "高棉风味凉拌牛肉", image: "/images/home/menu-03.webp", desc: "使用新鲜高棉香料调味的凉拌菜，酸辣清爽，刚好中和肉类的油腻感。" },
    { title: "麦片黄油炸大虾", image: "/images/home/menu-04.webp", desc: "选用肥美大虾，裹上酥脆麦片与黄油下锅大火快炸，香气十足。" },
    { title: "脆皮烧猪配软包", image: "/images/home/menu-05.webp", desc: "总铺师火候掌控的脆皮烤猪，皮脆肉嫩，搭配软包吃刚好解腻。" },
    { title: "秘制糖醋鱼", image: "/images/home/menu-06.webp", desc: "将鲜鱼炸至酥脆，淋上比例刚好的糖醋酱汁，是一道酸甜讨喜的大菜。" },
    { title: "猛火香辣鱼片", image: "/images/home/menu-07.webp", desc: "靠着大炉猛火快炒，让鱼片滑嫩入味，香辣下饭。" },
    { title: "十全珍品鲍鱼汤", image: "/images/home/menu-08.webp", desc: "用料大方的热汤，加上中药材慢火熬煮，喝起来温润舒服。" },
    { title: "凉拌剔骨鸭掌", image: "/images/home/menu-09.webp", desc: "手工去骨保留脆弹口感，拌入清爽的酸辣酱汁，是非常好的开胃菜。" },
    { title: "豉油皇火候蒸鱼", image: "/images/home/menu-10.webp", desc: "精确掌控清蒸时间，淋上甘甜酱油，吃的是新鲜鱼获的自然鲜味。" },
    { title: "古法荷叶飘香饭", image: "/images/home/menu-11.webp", desc: "把炒好的丰富配料与米饭用荷叶包起来蒸透，让荷叶清香完全入味。" },
    { title: "正宗港式明炉烧鸭", image: "/images/home/menu-12.webp", desc: "师傅烤制逼出多余油脂，外皮香脆、肉质多汁不干柴。" },
    { title: "传统高棉特色甜点", image: "/images/home/menu-13.webp", desc: "在地高棉风味甜品，用新鲜椰浆与斑斓叶制作，为办桌完美收尾。" },
    { title: "冬荫功野生大虾汤", image: "/images/home/menu-14.webp", desc: "道地的东南亚酸辣风味，搭配紧实弹牙的鲜虾，喝下去非常过瘾。" },
    { title: "金牌原只烤乳猪", image: "/images/home/menu-15.webp", desc: "办桌最顾面子的一道大菜，外皮金黄酥脆，肉质软嫩不油腻。" }
  ]
};

export interface BlogPost {
  title: string;
  subTitle: string;
  link: string;
  image: string;
}

export const blogPosts: Record<string, BlogPost[]> = {
  km: [
    { title: "ការវាយតម្លៃទីតាំង និងរៀបចំផ្លូវចេញម្ហូប", subTitle: "ការពិនិត្យកម្លាំងភ្លើង និងការរៀបចំរោងការជាមុន", link: "/km/blog/01-venue-logistics/", image: "/images/home/blog-wedding-service-guide.webp" },
    { title: "ការគ្រប់គ្រងការចេញម្ហូបរយតុ", subTitle: "ការរក្សាកម្តៅម្ហូប និងទប់ទល់នឹងអាកាសធាតុខាងក្រៅ", link: "/km/blog/02-event-party-planning/", image: "/images/home/blog-event-party-planning.webp" },
    { title: "ស្តង់ដារគុណភាព និងការរក្សាសាច់ស្រស់", subTitle: "ការរក្សាភាពត្រជាក់ ២៤ម៉ោង និងការកំណត់ស្តង់ដារគ្រឿងទេស", link: "/km/blog/03-chef-professional-standard/", image: "/images/home/blog-chef-professional-standard.webp" },
    { title: "ការធានាអនាម័យ និងសុវត្ថិភាពម្ហូបការ", subTitle: "ការបែងចែកសាច់ឆៅនិងឆ្អិនដាច់ពីគ្នា រួមទាំងប្រព័ន្ធទឹកស្អាត", link: "/km/blog/04-food-safety-quality/", image: "/images/home/blog-food-safety-quality.webp" },
    { title: "ការរៀបចំម៉ឺនុយម្ហូបការខ្មែរ-ចិន", subTitle: "បច្ចេកទេសបុកគ្រឿងដោយដៃ និងការរៀបចំរសជាតិមិនឱ្យទ្រាន់", link: "/km/blog/05-khmer-wedding-menu/", image: "/images/home/blog-khmer-wedding-menu.webp" },
    { title: "ការគ្រប់គ្រងហានិភ័យពេលកម្មវិធីផ្ទាល់", subTitle: "ការត្រៀមម៉ាស៊ីនភ្លើងបម្រុង និងការទប់ទល់នឹងកំណើនភ្ញៀវភ្លាមៗ", link: "/km/blog/06-service-process-sop/", image: "/images/home/blog-service-process-sop.webp" }
  ],
  en: [
    { title: "Venue Audits & Logistics", subTitle: "Electrical Loads & Temporary Structure Setup", link: "/en/blog/01-venue-logistics/", image: "/images/home/blog-wedding-service-guide.webp" },
    { title: "100-Table Capacity Control", subTitle: "Managing Heat Loss & Service Flow", link: "/en/blog/02-event-party-planning/", image: "/images/home/blog-event-party-planning.webp" },
    { title: "Sourcing & Cold Chain Defense", subTitle: "24-Hour Temperature Control & Batch Consistency", link: "/en/blog/03-chef-professional-standard/", image: "/images/home/blog-chef-professional-standard.webp" },
    { title: "Catering Food Safety", subTitle: "Cross-Contamination & The 75°C Kill Step", link: "/en/blog/04-food-safety-quality/", image: "/images/home/blog-food-safety-quality.webp" },
    { title: "Khmer-Chinese Menus", subTitle: "Flavor Sequencing & Palate Fatigue", link: "/en/blog/05-khmer-wedding-menu/", image: "/images/home/blog-khmer-wedding-menu.webp" },
    { title: "Execution & Contingency", subTitle: "Backup Generators & Extreme Weather Protocols", link: "/en/blog/06-service-process-sop/", image: "/images/home/blog-service-process-sop.webp" }
  ],
  zh: [
    { title: "办桌场地勘测与水电调度", subTitle: "应对户外空地与临时建筑的硬体条件", link: "/zh/blog/01-venue-logistics/", image: "/images/home/blog-wedding-service-guide.webp" },
    { title: "百桌大型办桌的出菜调度", subTitle: "对抗现场环境变数与保温暖热把控", link: "/zh/blog/02-event-party-planning/", image: "/images/home/blog-event-party-planning.webp" },
    { title: "外烩总铺师的食材与口味把关", subTitle: "低温保鲜机制与百桌大锅菜的口味稳定度", link: "/zh/blog/03-chef-professional-standard/", image: "/images/home/blog-chef-professional-standard.webp" },
    { title: "办桌现场的卫生与食安防线", subTitle: "生熟食物理隔离与 75°C 杀菌阈值", link: "/zh/blog/04-food-safety-quality/", image: "/images/home/blog-food-safety-quality.webp" },
    { title: "中柬混搭办桌菜单排版逻辑", subTitle: "手工高棉香料与口味轻重缓急的拿捏", link: "/zh/blog/05-khmer-wedding-menu/", image: "/images/home/blog-khmer-wedding-menu.webp" },
    { title: "现场统筹与突发状况对策", subTitle: "时间排程、动线清空与水电跳电准备", link: "/zh/blog/06-service-process-sop/", image: "/images/home/blog-service-process-sop.webp" }
  ]
};

import type { ImageMetadata } from 'astro';
import blogKhmerWeddingMenu from '../assets/images/home/blog-khmer-wedding-menu.webp';
import menu11 from '../assets/images/home/menu-11.webp';
import menu04 from '../assets/images/home/menu-04.webp';
import menu09 from '../assets/images/home/menu-09.webp';
import menu14 from '../assets/images/home/menu-14.webp';
import menu05 from '../assets/images/home/menu-05.webp';
import blogServiceProcessSop from '../assets/images/home/blog-service-process-sop.webp';
import menu01 from '../assets/images/home/menu-01.webp';
import menu06 from '../assets/images/home/menu-06.webp';
import blogFoodSafetyQuality from '../assets/images/home/blog-food-safety-quality.webp';
import menu07 from '../assets/images/home/menu-07.webp';
import menu10 from '../assets/images/home/menu-10.webp';
import menu12 from '../assets/images/home/menu-12.webp';
import heroLuxuryBanquetSetup from '../assets/images/home/hero-luxury-banquet-setup.webp';
import menu03 from '../assets/images/home/menu-03.webp';
import blogEventPartyPlanning from '../assets/images/home/blog-event-party-planning.webp';
import blogChefProfessionalStandard from '../assets/images/home/blog-chef-professional-standard.webp';
import menu08 from '../assets/images/home/menu-08.webp';
import menu15 from '../assets/images/home/menu-15.webp';
import brandCkmLogoGold from '../assets/images/home/brand-ckm-logo-gold.webp';
import menu02 from '../assets/images/home/menu-02.webp';
import blogWeddingServiceGuide from '../assets/images/home/blog-wedding-service-guide.webp';
import menu13 from '../assets/images/home/menu-13.webp';
import menu16 from '../assets/processed_images_ai/menu-16.png';

export const siteDomain = "https://ckmkh.com";
export const telegramLink = "https://t.me/CKMSam06";
export const facebookLink = "https://www.facebook.com/CKMFOODS";

export const heroImageRelative = heroLuxuryBanquetSetup;
export const logo = brandCkmLogoGold;

export const mainPhone = "011 827 782";

export const phoneNumbers = [
  { num: "011 827 782", type: "Cellcard", svg: `<svg class="w-5 h-5 md:w-6 md:h-6 text-amber-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="5" y="2" width="14" height="20" rx="2" ry="2"></rect><line x1="12" y1="18" x2="12.01" y2="18"></line></svg>` },
  { num: "012 977 696", type: "Cellcard", svg: `<svg class="w-5 h-5 md:w-6 md:h-6 text-amber-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path></svg>` },
  { num: "015 977 696", type: "Smart", svg: `<svg class="w-5 h-5 md:w-6 md:h-6 text-amber-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path><path d="M14.05 2a9 9 0 0 1 8 7.94"></path><path d="M14.05 6A5 5 0 0 1 18 10"></path></svg>` }
];

export interface MenuItem {
  title: string;
  image: ImageMetadata;
  desc: string;
  alt?: string;
}

// Khmer only — index.astro reads menuItems.km and nothing else. The en/zh
// translations that used to sit here were never rendered by any page.
export const menuItems: Record<string, MenuItem[]> = {
  km: [
    { title: "ម្ហូបក្លែម៦មុខ", image: menu01, desc: "ម្ហូបក្លែម៦មុខ រៀបចំយ៉ាងសម្រិតសម្រាំងសម្រាប់ភ្ញៀវហូបលេងមុនពេលម្ហូបធំចេញ ជួយឱ្យកាន់តែមានចំណង់អាហារ។", alt: "សេវាកម្មម្ហូបការ ភ្នំពេញ - ម្ហូបក្លែម៦មុខ ចេង គួងម៉េង" },
    { title: "ត្រីដប៊ុនបំពងស្រួយ", image: menu02, desc: "ប្រើប្រាស់ភ្លើង និងសីតុណ្ហភាពប្រេងបានត្រឹមត្រូវ ដើម្បីបំពងត្រីឱ្យស្រួយខាងក្រៅ តែសាច់ខាងក្នុងនៅតែទន់ផ្អែម និងមិនស្ងួត។", alt: "សេវាកម្មទទួលរៀបចំកម្មវិធី - ត្រីដប៊ុនបំពងស្រួយ CKM" },
    { title: "ភាសាច់គោក្រៅអង្គារ", image: menu03, desc: "សាច់គោអាំងឱ្យនៅទន់ល្មម យកមកភ្លាជាមួយក្រូចឆ្មារ និងម្ទេសស្រស់ បង្កើតជារសជាតិជូរហឹរឆ្ងាញ់ពិសា។", alt: "ចុងភៅរៀបចំម្ហូបការ - ភាសាច់គោក្រៅអង្គារ រសជាតិដើម" },
    { title: "បង្កងបំពងគ្រាប់ធញ្ញជាតិ", image: menu04, desc: "បង្កងទន្លេស្រស់ៗយកមកបំពងជាមួយគ្រាប់ធញ្ញជាតិ និងប៊័រ ដើម្បីឱ្យឡើងក្លិនឈ្ងុយ និងស្រួយឆ្ងាញ់។", alt: "ម៉ឺនុយម្ហូបការខ្មែរ-ចិន - បង្កងបំពងគ្រាប់ធញ្ញជាតិ" },
    { title: "ជ្រូកខ្វៃនិងនំប៉័ង", image: menu05, desc: "កូនជ្រូកខ្វៃដោយការគ្រប់គ្រងភ្លើងបានល្អ ធ្វើឱ្យស្បែកស្រួយរឹមៗ និងសាច់ផុយ ញ៉ាំផ្ទាប់ជាមួយនំប៉័ងទន់ៗ។", alt: "សេវាកម្មម្ហូបការតម្លៃសមរម្យ - ជ្រូកខ្វៃនិងនំប៉័ងពិសេស" },
    { title: "ត្រីតុកកែជូរអែម", image: menu06, desc: "ត្រីបំពងស្រួយ ស្រូបដោយទឹកជ្រលក់ដែលមានរសជាតិជូរអែមល្មម ឆ្ងាញ់ជាប់មាត់។", alt: "សេវាកម្មម្ហូបការ ភ្នំពេញ - ត្រីតុកកែជូរអែម ឆ្ងាញ់ជាប់មាត់" },
    { title: "ត្រីហឹរឡប់ពង", image: menu07, desc: "ប្រើប្រាស់បច្ចេកទេសឆាភ្លើងខ្លាំង ដើម្បីរឹតសាច់ត្រីឱ្យហាប់ និងបញ្ចេញក្លិនឈ្ងុយពីគ្រឿងទេសបានល្អបំផុត។", alt: "កញ្ចប់សេវាកម្មរៀបចំពិធីមង្គលការ - ត្រីហឹរឡប់ពង" },
    { title: "ស៊ុបប៉ាវហឺ១០មុខ", image: menu08, desc: "រម្ងាស់ដោយភ្លើងតិចៗរយៈពេលយូរ ជាមួយប៉ាវហឺ និងថ្នាំចិន១០មុខ ដើម្បីទាញយករសជាតិផ្អែមពីធម្មជាតិ និងប៉ូវកម្លាំង។", alt: "ទទួលរៀបចំអាហារប៊ូហ្វេ - ស៊ុបប៉ាវហឺ១០មុខ គុណភាពខ្ពស់" },
    { title: "ញាំជើងទាបង្គោរមិក", image: menu09, desc: "ជើងទាដកឆ្អឹងប្រកបដោយអនាម័យ យកមកញាំជូរហឹរស្រាលៗ ជួយកាត់បន្ថយភាពទ្រាន់ពីម្ហូបសាច់។", alt: "ចុងភៅរៀបចំម្ហូបការ - ញាំជើងទាបង្គោរមិក អនាម័យខ្ពស់" },
    { title: "ត្រីតុកកែចំហ៊ុយទឹកស៊ីអ៊ីវ", image: menu10, desc: "គ្រប់គ្រងពេលវេលាចំហុយបានយ៉ាងជាក់លាក់ ដើម្បីធានាថាសាច់ត្រីឆ្អិនល្អ តែនៅតែទន់រលោង ស្រូបជាមួយទឹកស៊ីអ៊ីវឈ្ងុយ។", alt: "សេវាកម្មទទួលរៀបចំកម្មវិធី - ត្រីតុកកែចំហ៊ុយទឹកស៊ីអ៊ីវ" },
    { title: "បាយខ្ចប់ស្លឹកឈូក", image: menu11, desc: "បាយឆាផ្សំគ្រឿង រុំក្នុងស្លឹកឈូក និងយកទៅចំហុយ ដើម្បីឱ្យក្លិនឈ្ងុយនៃស្លឹកឈូកជ្រាបចូលគ្រប់គ្រាប់បាយ។", alt: "ម៉ឺនុយម្ហូបការខ្មែរ-ចិន - បាយខ្ចប់ស្លឹកឈូកឈ្ងុយឆ្ងាញ់" },
    { title: "ទាខ្វៃហុងកុង", image: menu12, desc: "ឆ្លងកាត់ការសម្ងួតស្បែក និងខ្វៃក្នុងឡកម្តៅខ្ពស់ ដើម្បីឱ្យស្បែកទាឡើងស្រួយ និងសាច់នៅរក្សាជាតិទឹកល្អ។", alt: "សេវាកម្មម្ហូបការ ភ្នំពេញ - ទាខ្វៃហុងកុង ចេង គួងម៉េង" },
    { title: "បង្អែមខ្មែរបុរាណ", image: menu13, desc: "បង្អែមខ្មែរឈ្ងុយខ្ទិះដូង និងស្លឹកតើយស្រស់ ជាបង្អែមដ៏ស័ក្តិសមបំផុតសម្រាប់បិទបញ្ចប់កម្មវិធីជប់លៀង។", alt: "កញ្ចប់សេវាកម្មរៀបចំពិធីមង្គលការ - បង្អែមខ្មែរបុរាណ" },
    { title: "តុងយាំបង្កងទន្លេ", image: menu14, desc: "ស៊ុបតុងយាំបង្កងទន្លេដែលមានរសជាតិជូរហឹរដិត ជួយកាត់បន្ថយភាពទ្រាន់ និងធ្វើឱ្យអ្នកញ៉ាំបែកញើសស្រួលខ្លួន។", alt: "ទទួលរៀបចំអាហារប៊ូហ្វេ - តុងយាំបង្កងទន្លេ ជូរហឹរ" },
    { title: "កូនជ្រូកខ្វៃទាំងមូល", image: menu15, desc: "មុខម្ហូបលើកមុខមាត់ម្ចាស់កម្មវិធី ខ្វៃដោយបច្ចេកទេសបង្វិលស្មើភ្លើង ធ្វើឱ្យស្បែកស្រួយរឹមៗគ្រប់កន្លែង និងសាច់ទន់ឆ្ងាញ់។", alt: "ចុងភៅរៀបចំម្ហូបការ - កូនជ្រូកខ្វៃទាំងមូល ស្រួយឆ្ងាញ់" },
    { title: "សាច់គោឡុកឡាក់", image: menu16, desc: "វត្ថុធាតុដើមស្រស់ៗគុណភាពខ្ពស់ ផ្តល់ជូនរសជាតិសាច់គោឡុកឡាក់ដ៏ឈ្ងុយឆ្ងាញ់។", alt: "សេវាកម្មម្ហូបការ - សាច់គោឡុកឡាក់គុណភាពខ្ពស់" }
  ],
};

// BlogPost / blogPosts were removed: nothing imported them, and every link they
// held pointed at /km/blog/… and /zh/blog/… routes that no longer exist.

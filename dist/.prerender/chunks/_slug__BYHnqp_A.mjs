import { g as getCollection } from './_astro_content_OBtCAXZi.mjs';
import { Resvg } from '@resvg/resvg-js';
import satori from 'satori';

async function fetchFont(lang, text) {
  let fontName = "Noto Sans";
  let url = "";
  if (lang === "zh") {
    fontName = "Noto Serif SC";
    url = `https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@700;900&text=${encodeURIComponent(text)}CKMCatering辦桌實戰日誌%020`;
  } else if (lang === "km") {
    fontName = "Hanuman";
    url = `https://fonts.googleapis.com/css2?family=Hanuman:wght@700;900&text=${encodeURIComponent(text)}CKMCateringកំណត់ហេតុប្រតិបត្តិការម្ហូបការ%020`;
  } else {
    fontName = "Playfair Display";
    url = `https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&text=${encodeURIComponent(text)}CKMCateringLog%020`;
  }
  try {
    const css = await (await fetch(url)).text();
    const resource = css.match(/src: url\((.+)\) format\('(opentype|truetype)'\)/);
    if (resource && resource[1]) {
      const res = await fetch(resource[1]);
      return { fontData: await res.arrayBuffer(), fontName };
    }
  } catch (e) {
    console.error("Font fetch error for", lang, text, e);
  }
  if (lang === "zh") {
    const fullFontRes = await fetch("https://github.com/notofonts/noto-cjk/raw/main/Serif/Variable/TTF/NotoSerifSC-VF.ttf");
    return { fontData: await fullFontRes.arrayBuffer(), fontName: "Noto Serif SC" };
  } else if (lang === "km") {
    const fullFontRes = await fetch("https://github.com/googlefonts/hanuman/raw/main/fonts/ttf/Hanuman-Bold.ttf");
    return { fontData: await fullFontRes.arrayBuffer(), fontName: "Hanuman" };
  } else {
    const fullFontRes = await fetch("https://github.com/googlefonts/PlayfairDisplay/raw/main/fonts/variable/PlayfairDisplay%5Bwght%5D.ttf");
    return { fontData: await fullFontRes.arrayBuffer(), fontName: "Playfair Display" };
  }
}
async function getStaticPaths() {
  const blogEntries = await getCollection("blog");
  return blogEntries.map((entry) => {
    const entryId = entry.id.replace(/\.mdx?$/, "");
    const [lang, ...slugParts] = entryId.split("/");
    const slug = slugParts.join("/");
    return {
      params: { lang, slug },
      props: { entry, lang }
    };
  });
}
const translations = {
  km: { tag: "កំណត់ហេតុប្រតិបត្តិការម្ហូបការ", author: "ចុងភៅឯក ចេង គួងម៉េង" },
  zh: { tag: "办桌实战日志", author: "主厨 钟光明" },
  en: { tag: "Catering Operations Log", author: "Executive Chef Cheng Koung Meng" }
};
async function GET({ props }) {
  const { entry, lang } = props;
  const title = entry.data.seoTitle || entry.data.title;
  const t = translations[lang] || translations.en;
  const { fontData, fontName } = await fetchFont(lang, title + t.tag + t.author);
  const svg = await satori(
    {
      type: "div",
      props: {
        style: {
          height: "100%",
          width: "100%",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          backgroundColor: "#f8fafc",
          // slate-50
          backgroundImage: "linear-gradient(to bottom right, #fffbeb, #f8fafc)",
          // amber-50 to slate-50
          padding: "60px",
          fontFamily: `"${fontName}"`,
          border: "12px solid #f59e0b"
          // amber-500
        },
        children: [
          {
            type: "div",
            props: {
              style: {
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                gap: "32px",
                textAlign: "center",
                maxWidth: "1000px"
              },
              children: [
                {
                  type: "div",
                  props: {
                    style: {
                      display: "flex",
                      backgroundColor: "#f59e0b",
                      // amber-500
                      color: "#fff",
                      padding: "12px 24px",
                      borderRadius: "4px",
                      fontSize: "28px",
                      fontWeight: 900,
                      letterSpacing: "0.1em",
                      textTransform: "uppercase"
                    },
                    children: t.tag
                  }
                },
                {
                  type: "h1",
                  props: {
                    style: {
                      fontSize: "64px",
                      fontWeight: 900,
                      color: "#0f172a",
                      // slate-900
                      lineHeight: 1.3,
                      margin: 0
                    },
                    children: title
                  }
                },
                {
                  type: "div",
                  props: {
                    style: {
                      display: "flex",
                      alignItems: "center",
                      gap: "16px",
                      marginTop: "24px"
                    },
                    children: [
                      {
                        type: "span",
                        props: {
                          style: {
                            fontSize: "32px",
                            color: "#d97706",
                            // amber-600
                            fontWeight: 700
                          },
                          children: "CKM Catering"
                        }
                      },
                      {
                        type: "span",
                        props: {
                          style: { fontSize: "28px", color: "#94a3b8" },
                          // slate-400
                          children: "|"
                        }
                      },
                      {
                        type: "span",
                        props: {
                          style: {
                            fontSize: "28px",
                            color: "#475569",
                            // slate-600
                            fontWeight: 500
                          },
                          children: t.author
                        }
                      }
                    ]
                  }
                }
              ]
            }
          }
        ]
      }
    },
    {
      width: 1200,
      height: 630,
      fonts: [
        {
          name: fontName,
          data: fontData,
          weight: 900,
          style: "normal"
        }
      ]
    }
  );
  const resvg = new Resvg(svg, {
    fitTo: { mode: "width", value: 1200 }
  });
  const pngData = resvg.render();
  const pngBuffer = pngData.asPng();
  return new Response(new Uint8Array(pngBuffer), {
    headers: {
      "Content-Type": "image/png",
      "Cache-Control": "public, max-age=31536000, immutable"
    }
  });
}

const _page = /*#__PURE__*/Object.freeze(/*#__PURE__*/Object.defineProperty({
  __proto__: null,
  GET,
  getStaticPaths
}, Symbol.toStringTag, { value: 'Module' }));

const page = () => _page;

export { page };

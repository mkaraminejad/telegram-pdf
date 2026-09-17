import express from "express";
import path from "path";
import { fileURLToPath } from "url";
import { createServer as createViteServer } from "vite";
import { GoogleGenAI } from "@google/genai";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

async function startServer() {
  const app = express();
  const PORT = 3000;

  app.use(express.json({ limit: "50mb" }));

  // Lazy / Safe Gemini initialization (Server-side only)
  let aiClient: GoogleGenAI | null = null;
  function getGeminiClient(): GoogleGenAI | null {
    if (!aiClient && process.env.GEMINI_API_KEY) {
      aiClient = new GoogleGenAI({
        apiKey: process.env.GEMINI_API_KEY,
        httpOptions: {
          headers: {
            "User-Agent": "aistudio-build",
          },
        },
      });
    }
    return aiClient;
  }

  // 1. Health & Status
  app.get("/api/health", (req, res) => {
    res.json({
      status: "ok",
      hasGeminiKey: Boolean(process.env.GEMINI_API_KEY),
      model: "gemini-3.8-flash",
      port: PORT,
    });
  });

  // 2. AI Persian Document Conversion & Structure Extraction
  app.post("/api/convert-ai", async (req, res) => {
    try {
      const { text, imageBase64, mimeType } = req.body;
      const ai = getGeminiClient();

      const systemInstruction = `شما یک سیستم هوش مصنوعی خبره در استخراج و بازخوانی اسناد PDF و تصاویر متنی به زبان فارسی هستید.
وظایف اصلی شما:
۱. بازخوانی دقیق و کامل متن بدون کوچکترین وارونگی کلمات یا جداشدگی حروف (مانند تبدیل «س ل ا م» به «سلام» و اصلاح واژگان چپ‌به‌راست‌شده).
۲. استخراج ساختار سند به شکل زیر در قالب یک آرایه JSON معتبر:
   - تیترها: {"type": "heading", "level": 1 | 2 | 3, "text": "..."}
   - پاراگراف‌ها: {"type": "paragraph", "text": "..."}
   - لیست‌ها: {"type": "bullet", "text": "..."}
   - جداول: {"type": "table", "data": [["ستون ۱", "ستون ۲"], ["مقدار ۱", "مقدار ۲"]]}
۳. حفظ دقیق کلمات انگلیسی، اصطلاحات فنی، کدها، فرمول‌ها و اعداد بدون تغییر جهت.
۴. رعایت استاندارد نگارش فارسی: استفاده از « » برای گیومه، علامت سوال ؟، ویرگول ، و نیم‌فاصله‌های صحیح (می‌شود، کتاب‌ها، خانه‌ام).

پاسخ شما اکیداً باید فقط یک JSON Array معتبر بدون هرگونه توضیح اضافی یا پیش‌وند/پس‌وند مارک‌داون باشد.`;

      let rawResultText = "";

      if (ai) {
        const contentsParts: Array<any> = [];

        if (imageBase64) {
          contentsParts.push({
            inlineData: {
              mimeType: mimeType || "image/png",
              data: imageBase64.replace(/^data:image\/\w+;base64,/, ""),
            },
          });
        }

        const prompt = text
          ? `لطفاً متن زیر که از PDF استخراج شده و دارای به‌هم‌ریختگی، وارونگی یا شکستگی ساختار است را بازخوانی، تصحیح و به بلوک‌های ساختاریافته تبدیل کنید:\n\n${text}`
          : "لطفاً تصویر این صفحه از سند فارسی را با هوش مصنوعی بازخوانی کرده و ساختار آن را به صورت JSON استخراج فرمایید.";

        contentsParts.push({ text: prompt });

        const response = await ai.models.generateContent({
          model: "gemini-3.8-flash",
          contents: { parts: contentsParts },
          config: {
            systemInstruction,
            temperature: 0.1,
            responseMimeType: "application/json",
          },
        });

        rawResultText = response.text || "[]";
      } else {
        // Fallback rule-based simulator when no Gemini key is provided in dev
        const sampleBlocks = [
          {
            type: "heading",
            level: 1,
            text: "گزارش جامع استخراج هوشمند سند فارسی (حالت بدون کلید API)",
          },
          {
            type: "paragraph",
            text: "این نتیجه به وسیله نرمال‌ساز داخلی و موتور قاعده‌محور تولید شده است. برای فعال‌سازی کامل هوش مصنوعی دیداری چندوجهی، کلید GEMINI_API_KEY در فایل تنظیمات فعال است.",
          },
          {
            type: "paragraph",
            text: (text || "متن ورودی نمونه").replace(/[يك]/g, (m: string) => (m === "ي" ? "ی" : "ک")),
          },
        ];
        rawResultText = JSON.stringify(sampleBlocks);
      }

      // Clean markdown code blocks if any
      let cleaned = rawResultText.trim();
      if (cleaned.startsWith("```json")) cleaned = cleaned.slice(7);
      if (cleaned.startsWith("```")) cleaned = cleaned.slice(3);
      if (cleaned.endsWith("```")) cleaned = cleaned.slice(0, -3);
      cleaned = cleaned.trim();

      const blocks = JSON.parse(cleaned);

      res.json({
        success: true,
        aiPowered: Boolean(ai),
        model: "gemini-3.8-flash",
        blocks,
      });
    } catch (err: any) {
      console.error("AI Conversion endpoint error:", err);
      res.status(500).json({
        success: false,
        error: err.message || "خطا در پردازش هوش مصنوعی",
      });
    }
  });

  // Vite middleware for development vs Production Static files
  if (process.env.NODE_ENV !== "production") {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: "spa",
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(process.cwd(), "dist");
    app.use(express.static(distPath));
    app.get("*", (req, res) => {
      res.sendFile(path.join(distPath, "index.html"));
    });
  }

  app.listen(PORT, "0.0.0.0", () => {
    console.log(`Server running on http://0.0.0.0:${PORT}`);
  });
}

startServer();

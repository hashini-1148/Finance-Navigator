// Google AI Studio (Gemini) free models — matches Python reference exactly
export const AI_MODELS = [
  { id: "gemini-2.5-flash",      name: "Gemini 2.5 Flash  · Free · 10 RPM" },
  { id: "gemini-2.5-flash-lite", name: "Gemini 2.5 Flash Lite · Free · 15 RPM" },
  { id: "gemini-2.5-pro",        name: "Gemini 2.5 Pro  · Free · 5 RPM" },
  { id: "gemini-2.0-flash",      name: "Gemini 2.0 Flash  · Free" },
  { id: "gemini-1.5-flash",      name: "Gemini 1.5 Flash  · Free" },
  { id: "gemini-1.5-flash-8b",   name: "Gemini 1.5 Flash 8B · Free" },
  { id: "gemini-1.5-pro",        name: "Gemini 1.5 Pro  · Free" },
];

export const EXPENSE_CATEGORIES = [
  { id: "rent",          name: "Rent / EMI",           color: "var(--chart-2)" },
  { id: "food",          name: "Food & Groceries",      color: "var(--chart-1)" },
  { id: "transport",     name: "Transport",             color: "var(--chart-3)" },
  { id: "utilities",     name: "Electricity & Bills",   color: "var(--chart-4)" },
  { id: "mobile",        name: "Mobile / Internet",     color: "var(--chart-5)" },
  { id: "education",     name: "Education / Courses",   color: "var(--destructive)" },
  { id: "healthcare",    name: "Healthcare / Medicines", color: "var(--accent)" },
  { id: "entertainment", name: "OTT / Entertainment",   color: "var(--chart-3)" },
  { id: "shopping",      name: "Shopping",              color: "var(--chart-1)" },
  { id: "investment",    name: "SIP / Investments",     color: "var(--primary)" },
  { id: "insurance",     name: "Insurance / LIC",       color: "var(--chart-2)" },
  { id: "other",         name: "Other",                 color: "var(--muted-foreground)" },
];

export const SYSTEM_PROMPT = `You are PocketPro AI, an expert Indian personal finance advisor. You have access to the user's real financial data. Provide specific, actionable advice tailored to India — use Indian instruments like SIP, PPF, ELSS, NPS, FD, Section 80C/80D, HRA where relevant. All amounts in ₹ (Indian Rupee).

Structure every response with:
1) 📊 Quick Assessment — one-line summary of their financial health
2) ⚡ Top 3 Actions — specific, immediate steps they can take
3) 💰 Savings Opportunities — Indian-specific instruments and strategies
4) ⚠️ Risks — any red flags in their data
5) 🗓️ 30-Day Plan — concrete monthly steps

Be encouraging but realistic. Use markdown formatting with bold headers. Keep it concise and impactful.`;

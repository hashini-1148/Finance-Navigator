export const AI_MODELS = [
  { id: "gemini-2.0-flash", name: "Gemini 2.0 Flash" },
  { id: "gemini-2.0-flash-lite", name: "Gemini 2.0 Flash Lite" },
  { id: "gemini-1.5-flash", name: "Gemini 1.5 Flash" },
  { id: "gemini-1.5-flash-8b", name: "Gemini 1.5 Flash 8B" },
  { id: "gemini-1.5-pro", name: "Gemini 1.5 Pro" },
];

export const EXPENSE_CATEGORIES = [
  { id: "rent", name: "Rent / EMI", color: "var(--chart-2)" },
  { id: "food", name: "Food & Groceries", color: "var(--chart-1)" },
  { id: "transport", name: "Transport", color: "var(--chart-3)" },
  { id: "utilities", name: "Electricity & Bills", color: "var(--chart-4)" },
  { id: "mobile", name: "Mobile / Internet", color: "var(--chart-5)" },
  { id: "education", name: "Education / Courses", color: "var(--destructive)" },
  { id: "healthcare", name: "Healthcare / Medicines", color: "var(--accent)" },
  { id: "entertainment", name: "OTT / Entertainment", color: "var(--chart-3)" },
  { id: "shopping", name: "Shopping", color: "var(--chart-1)" },
  { id: "investment", name: "SIP / Investments", color: "var(--primary)" },
  { id: "insurance", name: "Insurance / LIC", color: "var(--chart-2)" },
  { id: "other", name: "Other", color: "var(--muted-foreground)" },
];

export const SYSTEM_PROMPT = `You are PocketPro, an expert Indian personal finance AI advisor embedded in a futuristic, sci-fi themed application. You understand the Indian financial ecosystem — Indian Rupee (₹), tax-saving instruments (PPF, ELSS, NPS, Section 80C), SIPs, EMIs, Provident Fund, and Indian cost of living. You analyze real user financial data and provide specific, actionable advice tailored to India.

Always structure your response with:
1) 📊 Quick Assessment
2) ⚡ Top 3 Immediate Actions
3) 💰 Savings Opportunities (mention Indian instruments like SIP, PPF, NPS, FD where relevant)
4) ⚠️ Risk Warnings (if any)
5) 🗓️ Monthly Action Plan

Use an encouraging but realistic tone. Format with clear sections using emojis as visual markers. Keep responses concise, impactful, and formatted with markdown. All currency values should use ₹ (Indian Rupee). Do not ask follow-up questions unless necessary — just provide the analysis based on the data.`;

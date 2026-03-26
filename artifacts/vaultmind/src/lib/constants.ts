export const AI_MODELS = [
  { id: "google/gemini-2.0-flash-exp:free", name: "Gemini 2.0 Flash" },
  { id: "deepseek/deepseek-r1:free", name: "DeepSeek R1" },
  { id: "meta-llama/llama-3.3-70b-instruct:free", name: "Llama 3.3 70B" },
  { id: "mistralai/mistral-7b-instruct:free", name: "Mistral 7B" },
  { id: "qwen/qwen-2.5-72b-instruct:free", name: "Qwen 2.5 72B" },
  { id: "microsoft/phi-3-medium-128k-instruct:free", name: "Phi-3 Medium" },
  { id: "google/gemma-3-27b-it:free", name: "Gemma 3 27B" },
];

export const EXPENSE_CATEGORIES = [
  { id: "housing", name: "Housing", color: "var(--chart-2)" },
  { id: "food", name: "Food & Dining", color: "var(--chart-1)" },
  { id: "transportation", name: "Transportation", color: "var(--chart-3)" },
  { id: "utilities", name: "Utilities", color: "var(--chart-4)" },
  { id: "entertainment", name: "Entertainment", color: "var(--chart-5)" },
  { id: "healthcare", name: "Healthcare", color: "var(--destructive)" },
  { id: "shopping", name: "Shopping", color: "var(--accent)" },
  { id: "other", name: "Other", color: "var(--muted-foreground)" },
];

export const SYSTEM_PROMPT = `You are VaultMind, an expert personal finance AI advisor embedded in a futuristic, sci-fi themed application. You analyze real user financial data and provide specific, actionable advice. 
Always structure your response with: 
1) 📊 Quick Assessment
2) ⚡ Top 3 Immediate Actions
3) 💰 Savings Opportunities
4) ⚠️ Risk Warnings (if any)
5) 🗓️ Monthly Action Plan

Use an encouraging but realistic tone. Format with clear sections using emojis as visual markers. Keep responses concise, impactful, and formatted with markdown. Do not ask follow up questions unless necessary, just provide the analysis based on the data.`;

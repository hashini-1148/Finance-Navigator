import { useState } from 'react';
import { useAppState } from './use-app-state';
import { SYSTEM_PROMPT } from '@/lib/constants';

type ChatMessage = { role: 'user' | 'assistant'; content: string };

const GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta/models";

export function useOpenRouter() {
  const { state } = useAppState();
  const [isPending, setIsPending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const getFinancialContextStr = () => {
    const totalExpenses = state.expenses.reduce((sum, e) => sum + e.budgeted, 0);
    const actualSpent = state.transactions.filter(t => t.type === 'expense').reduce((sum, t) => sum + t.amount, 0);
    return `
USER FINANCIAL CONTEXT (Indian Rupees ₹):
- Monthly Income: ₹${state.income.toLocaleString('en-IN')}
- Budgeted Expenses: ₹${totalExpenses.toLocaleString('en-IN')}
- Actual Spent (All Time): ₹${actualSpent.toLocaleString('en-IN')}
- Net Monthly Savings: ₹${(state.income - totalExpenses).toLocaleString('en-IN')}
- Savings Goals: ${state.goals.map(g => `${g.name} (₹${g.current.toLocaleString('en-IN')}/₹${g.target.toLocaleString('en-IN')})`).join(', ')}
- Budget Allocation: ${state.expenses.map(e => `${e.category}: ₹${e.budgeted.toLocaleString('en-IN')}`).join(', ')}
- Recent Transactions: ${state.transactions.slice(0, 8).map(t => `${t.description}: ₹${t.amount.toLocaleString('en-IN')} (${t.type})`).join(', ')}
    `.trim();
  };

  const askAi = async (prompt: string, messagesHistory: ChatMessage[] = [], modelOverride?: string): Promise<string> => {
    if (!state.settings.apiKey) {
      const err = "Google AI Studio API key is missing. Click 'Set API Key' to add it.";
      setError(err);
      throw new Error(err);
    }

    setIsPending(true);
    setError(null);

    const model = modelOverride || state.settings.selectedModel;
    const systemInstruction = SYSTEM_PROMPT + '\n\n' + getFinancialContextStr();

    // Build Gemini-format contents array (role: "user" | "model")
    // Skip the initial greeting from assistant history to avoid role conflict
    const geminiContents = messagesHistory
      .filter((_, i) => i > 0) // skip first assistant greeting
      .map(m => ({
        role: m.role === 'assistant' ? 'model' : 'user',
        parts: [{ text: m.content }]
      }));

    // Append current user prompt
    geminiContents.push({ role: 'user', parts: [{ text: prompt }] });

    const body = {
      systemInstruction: { parts: [{ text: systemInstruction }] },
      contents: geminiContents,
      generationConfig: {
        temperature: 0.7,
        maxOutputTokens: 1500,
      }
    };

    try {
      const url = `${GEMINI_API_BASE}/${model}:generateContent?key=${state.settings.apiKey}`;
      const response = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body)
      });

      if (!response.ok) {
        const errData = await response.json();
        const msg = errData?.error?.message || `API error ${response.status}`;
        throw new Error(msg);
      }

      const data = await response.json();
      const text = data?.candidates?.[0]?.content?.parts?.[0]?.text;
      if (!text) throw new Error("Empty response from Gemini.");
      return text as string;

    } catch (err: any) {
      setError(err.message);
      throw err;
    } finally {
      setIsPending(false);
    }
  };

  const compareModels = async (prompt: string, models: string[]) => {
    if (!state.settings.apiKey) {
      throw new Error("Google AI Studio API key is missing.");
    }
    setIsPending(true);
    setError(null);
    try {
      const results = await Promise.all(
        models.map(async (model) => {
          const startTime = Date.now();
          const content = await askAi(prompt, [], model);
          return { model, content, duration: Date.now() - startTime };
        })
      );
      return results;
    } catch (err: any) {
      setError(err.message);
      throw err;
    } finally {
      setIsPending(false);
    }
  };

  return { askAi, compareModels, isPending, error };
}

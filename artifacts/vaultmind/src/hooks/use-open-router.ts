import { useState } from 'react';
import { useAppState } from './use-app-state';
import { SYSTEM_PROMPT, AI_MODELS } from '@/lib/constants';

type ChatMessage = { role: 'user' | 'assistant'; content: string };

// Google AI Studio free endpoint — same as Python reference
const GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta/models";

const VALID_MODEL_IDS = new Set([
  "gemini-2.5-flash",
  "gemini-2.5-flash-lite",
  "gemini-2.5-pro",
  "gemini-2.0-flash",
  "gemini-2.0-flash-lite",
  "gemini-1.5-flash",
  "gemini-1.5-flash-8b",
  "gemini-1.5-pro",
]);

function friendlyError(status: number, raw: string): string {
  if (status === 400) return "Bad request — the model name may be invalid. Try Gemini 2.5 Flash.";
  if (status === 403) return "Invalid API key — check your Google AI Studio key (get one free at aistudio.google.com/app/apikey).";
  if (status === 429) return "Rate limit reached — free tier is 10 req/min. Wait a moment or switch to Gemini 2.5 Flash-Lite (15 RPM).";
  if (status === 404) return "Model not found — this model may require billing. Switch to Gemini 2.5 Flash (free).";
  if (status === 500) return "Gemini server error — try again in a moment.";
  return raw || `API error ${status}`;
}

export function useOpenRouter() {
  const { state } = useAppState();
  const [isPending, setIsPending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Check if the stored API key looks like an OpenRouter key (won't work with Gemini)
  const isOpenRouterKey = state.settings.apiKey.startsWith('sk-or-');
  const effectiveKey = isOpenRouterKey ? '' : state.settings.apiKey;

  // Fall back to default model if stored model is an OpenRouter model ID
  const effectiveModel = (modelId: string) => {
    if (VALID_MODEL_IDS.has(modelId)) return modelId;
    return AI_MODELS[0].id; // default: gemini-2.5-flash
  };

  const getFinancialContext = () => {
    const totalExpenses = state.expenses.reduce((sum, e) => sum + e.budgeted, 0);
    const actualSpent = state.transactions.filter(t => t.type === 'expense').reduce((sum, t) => sum + t.amount, 0);
    return [
      `FINANCIAL CONTEXT (Indian Rupees ₹):`,
      `- Monthly Income: ₹${state.income.toLocaleString('en-IN')}`,
      `- Budgeted Expenses: ₹${totalExpenses.toLocaleString('en-IN')}`,
      `- Net Monthly Savings: ₹${(state.income - totalExpenses).toLocaleString('en-IN')}`,
      `- Actual Spent (all-time): ₹${actualSpent.toLocaleString('en-IN')}`,
      `- Budget Breakdown: ${state.expenses.map(e => `${e.category} ₹${e.budgeted.toLocaleString('en-IN')}`).join(' | ')}`,
      `- Goals: ${state.goals.map(g => `${g.name} (saved ₹${g.current.toLocaleString('en-IN')} of ₹${g.target.toLocaleString('en-IN')})`).join(' | ')}`,
      `- Last 8 transactions: ${state.transactions.slice(0, 8).map(t => `${t.description} ₹${t.amount.toLocaleString('en-IN')} (${t.type})`).join(', ')}`,
    ].join('\n');
  };

  const askAi = async (prompt: string, messagesHistory: ChatMessage[] = [], modelOverride?: string): Promise<string> => {
    if (!effectiveKey) {
      const msg = isOpenRouterKey
        ? "That looks like an OpenRouter key (sk-or-...). Please enter a Google AI Studio key from aistudio.google.com/app/apikey"
        : "Add your Google AI Studio API key to start — click 'Set Gemini Key' above.";
      setError(msg);
      throw new Error(msg);
    }

    setIsPending(true);
    setError(null);

    const model = effectiveModel(modelOverride || state.settings.selectedModel);

    // Build the full prompt as one text part (same as Python reference)
    // Include conversation history as plain text context
    const historyText = messagesHistory.length > 1
      ? '\n\nCONVERSATION HISTORY:\n' +
        messagesHistory
          .slice(1) // skip opening greeting
          .map(m => `${m.role === 'user' ? 'User' : 'PocketPro AI'}: ${m.content}`)
          .join('\n\n')
      : '';

    const fullPrompt = `${SYSTEM_PROMPT}\n\n${getFinancialContext()}${historyText}\n\nUser: ${prompt}`;

    // Payload matches Python gemini_call exactly
    const payload = {
      contents: [{ parts: [{ text: fullPrompt }] }],
      generationConfig: { temperature: 0.3, maxOutputTokens: 2000 },
    };

    try {
      const url = `${GEMINI_API_BASE}/${model}:generateContent?key=${effectiveKey}`;
      const response = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        let rawMsg = `API error ${response.status}`;
        try {
          const errData = await response.json();
          rawMsg = errData?.error?.message || rawMsg;
        } catch (_) {}
        throw new Error(friendlyError(response.status, rawMsg));
      }

      const data = await response.json();
      // Same extraction path as Python: data["candidates"][0]["content"]["parts"][0]["text"]
      const text = data?.candidates?.[0]?.content?.parts?.[0]?.text;
      if (!text) throw new Error(`Unexpected response from Gemini: ${JSON.stringify(data).slice(0, 200)}`);
      return text as string;

    } catch (err: any) {
      setError(err.message);
      throw err;
    } finally {
      setIsPending(false);
    }
  };

  const compareModels = async (prompt: string, models: string[]) => {
    if (!effectiveKey) throw new Error("Google AI Studio API key is missing.");
    setIsPending(true);
    setError(null);
    try {
      const results = await Promise.all(
        models.map(async (model) => {
          const t0 = Date.now();
          const content = await askAi(prompt, [], model);
          return { model, content, duration: Date.now() - t0 };
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

  return { askAi, compareModels, isPending, error, isKeyInvalid: !effectiveKey };
}

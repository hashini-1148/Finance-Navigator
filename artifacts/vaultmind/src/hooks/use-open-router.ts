import { useState } from 'react';
import { useAppState } from './use-app-state';
import { SYSTEM_PROMPT } from '@/lib/constants';

type Message = {
  role: 'system' | 'user' | 'assistant';
  content: string;
};

export function useOpenRouter() {
  const { state } = useAppState();
  const [isPending, setIsPending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const getFinancialContextStr = () => {
    const totalExpenses = state.expenses.reduce((sum, e) => sum + e.budgeted, 0);
    const actualSpent = state.transactions.filter(t => t.type === 'expense').reduce((sum, t) => sum + t.amount, 0);
    
    return `
    USER FINANCIAL CONTEXT:
    - Monthly Income: $${state.income}
    - Budgeted Expenses: $${totalExpenses}
    - Actual Spent (All Time): $${actualSpent}
    - Savings Goals: ${state.goals.map(g => `${g.name} ($${g.current}/$${g.target})`).join(', ')}
    - Recent Transactions: ${state.transactions.slice(0, 5).map(t => `${t.date}: ${t.description} ($${t.amount})`).join(', ')}
    `;
  };

  const askAi = async (prompt: string, messagesHistory: Message[] = [], modelOverride?: string) => {
    if (!state.settings.apiKey) {
      throw new Error("OpenRouter API Key is missing. Please add it in settings.");
    }

    setIsPending(true);
    setError(null);

    const model = modelOverride || state.settings.selectedModel;
    
    const messages: Message[] = [
      { role: 'system', content: SYSTEM_PROMPT + '\n' + getFinancialContextStr() },
      ...messagesHistory,
      { role: 'user', content: prompt }
    ];

    try {
      const response = await fetch("https://openrouter.ai/api/v1/chat/completions", {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${state.settings.apiKey}`,
          "Content-Type": "application/json",
          "HTTP-Referer": window.location.href,
          "X-Title": "VaultMind Finance Assistant"
        },
        body: JSON.stringify({
          model: model,
          messages: messages,
        })
      });

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.error?.message || "Failed to fetch AI response");
      }

      const data = await response.json();
      return data.choices[0].message.content as string;

    } catch (err: any) {
      setError(err.message);
      throw err;
    } finally {
      setIsPending(false);
    }
  };

  const compareModels = async (prompt: string, models: string[]) => {
    if (!state.settings.apiKey) {
      throw new Error("OpenRouter API Key is missing.");
    }
    
    setIsPending(true);
    setError(null);

    try {
      const promises = models.map(async (model) => {
        const startTime = Date.now();
        const content = await askAi(prompt, [], model);
        const duration = Date.now() - startTime;
        return { model, content, duration };
      });

      const results = await Promise.all(promises);
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

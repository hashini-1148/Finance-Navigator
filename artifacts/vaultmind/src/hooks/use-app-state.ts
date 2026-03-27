import { useState, useEffect, createContext, useContext } from 'react';
import { v4 as uuidv4 } from 'uuid';

export type Transaction = {
  id: string;
  date: string;
  description: string;
  category: string;
  amount: number;
  type: 'income' | 'expense';
};

export type Goal = {
  id: string;
  name: string;
  target: number;
  current: number;
  targetDate: string;
  priority: 'Emergency Fund' | 'Vacation' | 'Home' | 'Investment' | 'Other';
};

export type BudgetCategory = {
  id: string;
  category: string;
  budgeted: number;
};

export type AppState = {
  income: number;
  expenses: BudgetCategory[];
  goals: Goal[];
  transactions: Transaction[];
  settings: {
    apiKey: string;
    selectedModel: string;
    onboardingComplete: boolean;
  };
};

const defaultState: AppState = {
  income: 75000,
  expenses: [
    { id: uuidv4(), category: 'Rent / EMI', budgeted: 18000 },
    { id: uuidv4(), category: 'Food & Groceries', budgeted: 8000 },
    { id: uuidv4(), category: 'Transport', budgeted: 4000 },
    { id: uuidv4(), category: 'Electricity & Bills', budgeted: 3000 },
    { id: uuidv4(), category: 'Mobile / Internet', budgeted: 999 },
    { id: uuidv4(), category: 'SIP / Investments', budgeted: 10000 },
  ],
  goals: [
    { id: uuidv4(), name: 'Emergency Fund (6 months)', target: 450000, current: 180000, targetDate: '2026-12-31', priority: 'Emergency Fund' },
    { id: uuidv4(), name: 'Home Down Payment', target: 2000000, current: 250000, targetDate: '2028-06-30', priority: 'Home' },
  ],
  transactions: [
    { id: uuidv4(), date: new Date().toISOString(), description: 'Monthly Salary', category: 'Income', amount: 75000, type: 'income' },
    { id: uuidv4(), date: new Date().toISOString(), description: 'Rent', category: 'Rent / EMI', amount: 18000, type: 'expense' },
    { id: uuidv4(), date: new Date().toISOString(), description: 'Big Basket Groceries', category: 'Food & Groceries', amount: 3200, type: 'expense' },
    { id: uuidv4(), date: new Date().toISOString(), description: 'Zerodha SIP', category: 'SIP / Investments', amount: 10000, type: 'expense' },
    { id: uuidv4(), date: new Date().toISOString(), description: 'Metro + Ola', category: 'Transport', amount: 1800, type: 'expense' },
  ],
  settings: {
    apiKey: '',
    selectedModel: 'gemini-2.5-flash',
    onboardingComplete: false,
  }
};

type AppStateContextType = {
  state: AppState;
  updateState: (updates: Partial<AppState> | ((prev: AppState) => AppState)) => void;
  updateSettings: (updates: Partial<AppState['settings']>) => void;
  addTransaction: (t: Omit<Transaction, 'id'>) => void;
  deleteTransaction: (id: string) => void;
  addGoal: (g: Omit<Goal, 'id'>) => void;
  updateGoal: (id: string, updates: Partial<Goal>) => void;
  deleteGoal: (id: string) => void;
  updateBudget: (id: string, budgeted: number) => void;
  addBudgetCategory: (category: string, budgeted: number) => void;
  deleteBudgetCategory: (id: string) => void;
  resetData: () => void;
};

const AppStateContext = createContext<AppStateContextType | undefined>(undefined);

export function useAppState() {
  const context = useContext(AppStateContext);
  if (!context) throw new Error('useAppState must be used within AppStateProvider');
  return context;
}

const VALID_GEMINI_MODELS = new Set([
  "gemini-2.5-flash", "gemini-2.5-flash-lite", "gemini-2.5-pro",
  "gemini-2.0-flash", "gemini-2.0-flash-lite",
  "gemini-1.5-flash", "gemini-1.5-flash-8b", "gemini-1.5-pro",
]);

function migrateSettings(settings: AppState['settings']): AppState['settings'] {
  // Clear OpenRouter keys (sk-or-v1-...) — they don't work with Gemini
  const apiKey = settings.apiKey?.startsWith('sk-or-') ? '' : (settings.apiKey || '');
  // Reset invalid model IDs (old OpenRouter model slugs like google/gemini-2.0-flash-exp:free)
  const selectedModel = VALID_GEMINI_MODELS.has(settings.selectedModel)
    ? settings.selectedModel
    : 'gemini-2.5-flash';
  return { ...settings, apiKey, selectedModel };
}

export function useAppStateInit() {
  const [state, setState] = useState<AppState>(() => {
    try {
      const saved = localStorage.getItem('vaultmind_state');
      if (saved) {
        const parsed = JSON.parse(saved);
        return {
          ...defaultState,
          ...parsed,
          // Deep merge settings with migration
          settings: migrateSettings({ ...defaultState.settings, ...(parsed.settings || {}) }),
        };
      }
    } catch (e) {
      console.error('Failed to load state', e);
    }
    return defaultState;
  });

  useEffect(() => {
    localStorage.setItem('vaultmind_state', JSON.stringify(state));
  }, [state]);

  const updateState = (updates: Partial<AppState> | ((prev: AppState) => AppState)) => {
    setState((prev) => {
      const next = typeof updates === 'function' ? updates(prev) : { ...prev, ...updates };
      return next;
    });
  };

  const updateSettings = (updates: Partial<AppState['settings']>) => {
    setState((prev) => ({ ...prev, settings: { ...prev.settings, ...updates } }));
  };

  const addTransaction = (t: Omit<Transaction, 'id'>) => {
    setState((prev) => ({
      ...prev,
      transactions: [{ ...t, id: uuidv4() }, ...prev.transactions]
    }));
  };

  const deleteTransaction = (id: string) => {
    setState((prev) => ({
      ...prev,
      transactions: prev.transactions.filter(t => t.id !== id)
    }));
  };

  const addGoal = (g: Omit<Goal, 'id'>) => {
    setState((prev) => ({
      ...prev,
      goals: [...prev.goals, { ...g, id: uuidv4() }]
    }));
  };

  const updateGoal = (id: string, updates: Partial<Goal>) => {
    setState((prev) => ({
      ...prev,
      goals: prev.goals.map(g => g.id === id ? { ...g, ...updates } : g)
    }));
  };

  const deleteGoal = (id: string) => {
    setState((prev) => ({
      ...prev,
      goals: prev.goals.filter(g => g.id !== id)
    }));
  };

  const updateBudget = (id: string, budgeted: number) => {
    setState((prev) => ({
      ...prev,
      expenses: prev.expenses.map(e => e.id === id ? { ...e, budgeted } : e)
    }));
  };

  const addBudgetCategory = (category: string, budgeted: number) => {
    setState((prev) => ({
      ...prev,
      expenses: [...prev.expenses, { id: uuidv4(), category, budgeted }]
    }));
  };

  const deleteBudgetCategory = (id: string) => {
    setState((prev) => ({
      ...prev,
      expenses: prev.expenses.filter(e => e.id !== id)
    }));
  };

  const resetData = () => setState(defaultState);

  return {
    state,
    updateState,
    updateSettings,
    addTransaction,
    deleteTransaction,
    addGoal,
    updateGoal,
    deleteGoal,
    updateBudget,
    addBudgetCategory,
    deleteBudgetCategory,
    resetData,
  };
}

export { AppStateContext };

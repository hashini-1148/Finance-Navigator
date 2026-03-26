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
  income: 5000,
  expenses: [
    { id: uuidv4(), category: 'Housing', budgeted: 1500 },
    { id: uuidv4(), category: 'Food & Dining', budgeted: 600 },
    { id: uuidv4(), category: 'Transportation', budgeted: 400 },
    { id: uuidv4(), category: 'Utilities', budgeted: 300 },
  ],
  goals: [
    { id: uuidv4(), name: 'Emergency Fund', target: 10000, current: 4500, targetDate: '2025-12-31', priority: 'Emergency Fund' }
  ],
  transactions: [
    { id: uuidv4(), date: new Date().toISOString(), description: 'Salary', category: 'Income', amount: 5000, type: 'income' },
    { id: uuidv4(), date: new Date().toISOString(), description: 'Rent', category: 'Housing', amount: 1500, type: 'expense' },
    { id: uuidv4(), date: new Date().toISOString(), description: 'Groceries', category: 'Food & Dining', amount: 120, type: 'expense' },
  ],
  settings: {
    apiKey: '',
    selectedModel: 'google/gemini-2.0-flash-exp:free',
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

export function useAppStateInit() {
  const [state, setState] = useState<AppState>(() => {
    try {
      const saved = localStorage.getItem('vaultmind_state');
      if (saved) return { ...defaultState, ...JSON.parse(saved) };
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

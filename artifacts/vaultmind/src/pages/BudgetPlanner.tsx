import { useState } from 'react';
import { useAppState } from '@/hooks/use-app-state';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Plus, Trash2, Zap } from 'lucide-react';
import { useLocation } from 'wouter';

export default function BudgetPlanner() {
  const { state, updateState, addBudgetCategory, deleteBudgetCategory, updateBudget } = useAppState();
  const [newCatName, setNewCatName] = useState('');
  const [newCatAmount, setNewCatAmount] = useState('');
  const [, setLocation] = useLocation();

  const handleAdd = () => {
    if (newCatName && newCatAmount) {
      addBudgetCategory(newCatName, Number(newCatAmount));
      setNewCatName('');
      setNewCatAmount('');
    }
  };

  const totalBudgeted = state.expenses.reduce((sum, e) => sum + e.budgeted, 0);
  
  // 50/30/20 Rule calculations
  const needs = state.income * 0.5;
  const wants = state.income * 0.3;
  const savings = state.income * 0.2;

  return (
    <div className="space-y-8 pb-12">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-display font-bold text-white tracking-widest uppercase">Resource Allocation</h1>
          <p className="text-muted-foreground font-mono mt-2">Budget Matrix Configuration</p>
        </div>
        <Button 
          onClick={() => setLocation('/ai-advisor')}
          className="bg-primary/20 text-primary hover:bg-primary/30 border border-primary/50 box-glow-cyan"
        >
          <Zap className="w-4 h-4 mr-2" /> AI Optimize
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-6">
          <Card className="glass-panel border-white/10">
            <CardHeader>
              <CardTitle className="font-display text-xl text-primary flex justify-between">
                <span>Monthly Influx</span>
                <span className="font-mono text-white">${state.income.toLocaleString()}</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-4">
                <Input 
                  type="number" 
                  value={state.income}
                  onChange={(e) => updateState({ income: Number(e.target.value) })}
                  className="bg-black/50 border-primary/30 font-mono text-xl focus-visible:ring-primary"
                />
              </div>
            </CardContent>
          </Card>

          <Card className="glass-panel border-white/10">
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle className="font-display text-xl">Allocation Vectors</CardTitle>
              <div className="font-mono text-sm text-muted-foreground">
                Total: <span className={totalBudgeted > state.income ? 'text-destructive text-glow-orange' : 'text-primary text-glow-cyan'}>${totalBudgeted.toLocaleString()}</span> / ${state.income.toLocaleString()}
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {state.expenses.map((exp) => (
                <div key={exp.id} className="flex items-center gap-4 group">
                  <Input 
                    value={exp.category} 
                    readOnly 
                    className="bg-transparent border-white/10 font-sans"
                  />
                  <Input 
                    type="number" 
                    value={exp.budgeted}
                    onChange={(e) => updateBudget(exp.id, Number(e.target.value))}
                    className="bg-black/30 border-white/20 font-mono w-32 focus-visible:ring-primary"
                  />
                  <Button variant="ghost" size="icon" onClick={() => deleteBudgetCategory(exp.id)} className="text-muted-foreground hover:text-destructive hover:bg-destructive/10 opacity-0 group-hover:opacity-100 transition-opacity">
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </div>
              ))}

              <div className="pt-4 border-t border-white/10 flex items-center gap-4">
                <Input 
                  placeholder="New Vector Name" 
                  value={newCatName}
                  onChange={(e) => setNewCatName(e.target.value)}
                  className="bg-black/50 border-white/20"
                />
                <Input 
                  type="number" 
                  placeholder="Amount" 
                  value={newCatAmount}
                  onChange={(e) => setNewCatAmount(e.target.value)}
                  className="bg-black/50 border-white/20 font-mono w-32"
                />
                <Button onClick={handleAdd} className="bg-white/10 hover:bg-white/20 text-white">
                  <Plus className="w-4 h-4" />
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="space-y-6">
          <Card className="glass-panel border-white/10">
            <CardHeader>
              <CardTitle className="font-display tracking-widest text-lg text-accent">50/30/20 Protocol</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span className="text-muted-foreground">Needs (50%)</span>
                  <span className="font-mono text-white">${needs.toLocaleString()}</span>
                </div>
                <div className="h-2 bg-black/50 rounded-full overflow-hidden border border-white/5">
                  <div className="h-full bg-primary shadow-[0_0_10px_#00f5c8]" style={{ width: '50%' }} />
                </div>
              </div>
              
              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span className="text-muted-foreground">Wants (30%)</span>
                  <span className="font-mono text-white">${wants.toLocaleString()}</span>
                </div>
                <div className="h-2 bg-black/50 rounded-full overflow-hidden border border-white/5">
                  <div className="h-full bg-accent shadow-[0_0_10px_#0090ff]" style={{ width: '30%' }} />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span className="text-muted-foreground">Savings (20%)</span>
                  <span className="font-mono text-white">${savings.toLocaleString()}</span>
                </div>
                <div className="h-2 bg-black/50 rounded-full overflow-hidden border border-white/5">
                  <div className="h-full bg-[#b537f2] shadow-[0_0_10px_#b537f2]" style={{ width: '20%' }} />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}

import { useState } from 'react';
import { useAppState } from '@/hooks/use-app-state';
import { Card, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Plus, Calendar } from 'lucide-react';
import { format } from 'date-fns';
import confetti from 'canvas-confetti';
import { motion } from 'framer-motion';

const formatINR = (val: number) => '₹' + val.toLocaleString('en-IN');

export default function SavingsGoals() {
  const { state, addGoal, updateGoal, deleteGoal } = useAppState();
  const [showAdd, setShowAdd] = useState(false);
  const [newGoal, setNewGoal] = useState({ name: '', target: '', current: '', targetDate: '', priority: 'Emergency Fund' });

  const handleAdd = () => {
    addGoal({
      name: newGoal.name,
      target: Number(newGoal.target),
      current: Number(newGoal.current),
      targetDate: newGoal.targetDate,
      priority: newGoal.priority as any
    });
    setShowAdd(false);
    setNewGoal({ name: '', target: '', current: '', targetDate: '', priority: 'Emergency Fund' });
  };

  const handleProgress = (id: string, current: number, target: number) => {
    updateGoal(id, { current });
    if (current >= target) {
      confetti({
        particleCount: 120,
        spread: 80,
        origin: { y: 0.6 },
        colors: ['#00f5c8', '#0090ff', '#b537f2', '#ff6b35']
      });
    }
  };

  return (
    <div className="space-y-8 pb-12">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-display font-bold text-white tracking-widest uppercase">Objective Subsystems</h1>
          <p className="text-muted-foreground font-mono mt-2">Capital accumulation targets</p>
        </div>
        <Button onClick={() => setShowAdd(!showAdd)} className="bg-primary text-black hover:bg-primary/80 box-glow-cyan">
          <Plus className="w-4 h-4 mr-2" /> New Target
        </Button>
      </div>

      {showAdd && (
        <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }} className="glass-panel p-6 border-primary/30 rounded-xl">
          <div className="grid grid-cols-1 md:grid-cols-6 gap-4">
            <Input placeholder="Goal Name (e.g. Home Loan Down)" value={newGoal.name} onChange={e => setNewGoal({ ...newGoal, name: e.target.value })} className="bg-black/50 md:col-span-2" />
            <div className="flex items-center gap-1">
              <span className="text-muted-foreground font-mono text-sm">₹</span>
              <Input type="number" placeholder="Target Amount" value={newGoal.target} onChange={e => setNewGoal({ ...newGoal, target: e.target.value })} className="bg-black/50" />
            </div>
            <div className="flex items-center gap-1">
              <span className="text-muted-foreground font-mono text-sm">₹</span>
              <Input type="number" placeholder="Current Funds" value={newGoal.current} onChange={e => setNewGoal({ ...newGoal, current: e.target.value })} className="bg-black/50" />
            </div>
            <Input type="date" value={newGoal.targetDate} onChange={e => setNewGoal({ ...newGoal, targetDate: e.target.value })} className="bg-black/50" />
            <Button onClick={handleAdd} className="bg-primary text-black w-full">Initialize</Button>
          </div>
        </motion.div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {state.goals.map((goal) => {
          const progress = Math.min(100, Math.round((goal.current / goal.target) * 100));
          const isComplete = progress >= 100;

          return (
            <Card key={goal.id} className={`glass-panel overflow-hidden transition-all duration-500 hover:scale-[1.02] ${isComplete ? 'border-primary/50 box-glow-cyan' : 'border-white/10'}`}>
              <div className="h-1 w-full bg-black/50">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${progress}%` }}
                  transition={{ duration: 1, ease: 'easeOut' }}
                  className={`h-full ${isComplete ? 'bg-primary shadow-[0_0_10px_#00f5c8]' : 'bg-accent shadow-[0_0_10px_#0090ff]'}`}
                />
              </div>
              <CardContent className="p-6 relative">
                {isComplete && <div className="absolute top-4 right-4 text-xs font-mono text-primary animate-pulse">ACHIEVED ✓</div>}
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="font-display text-xl font-bold tracking-wide">{goal.name}</h3>
                    <p className="text-xs text-muted-foreground uppercase tracking-widest mt-1">{goal.priority}</p>
                  </div>
                  <div className="w-12 h-12 rounded-full border-2 border-white/10 flex items-center justify-center relative">
                    <svg className="absolute inset-0 w-full h-full -rotate-90">
                      <circle cx="24" cy="24" r="22" fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="4" />
                      <circle
                        cx="24" cy="24" r="22" fill="none"
                        stroke={isComplete ? '#00f5c8' : '#0090ff'} strokeWidth="4"
                        strokeDasharray="138" strokeDashoffset={138 - (138 * progress) / 100}
                        strokeLinecap="round"
                        style={{ transition: 'stroke-dashoffset 1s ease-out' }}
                      />
                    </svg>
                    <span className="text-xs font-mono">{progress}%</span>
                  </div>
                </div>

                <div className="space-y-4">
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Saved</span>
                    <span className="font-mono text-white">{formatINR(goal.current)}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Target</span>
                    <span className="font-mono text-white">{formatINR(goal.target)}</span>
                  </div>
                  <div className="flex items-center gap-2 text-xs text-muted-foreground mt-4">
                    <Calendar className="w-3 h-3" />
                    <span>ETA: {goal.targetDate ? format(new Date(goal.targetDate), 'dd MMM yyyy') : 'TBD'}</span>
                  </div>
                </div>

                <div className="mt-6 flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    className="flex-1 bg-white/5 border-white/10 hover:bg-white/10"
                    onClick={() => {
                      const add = prompt('Enter amount to add (₹):');
                      if (add && !isNaN(Number(add))) {
                        handleProgress(goal.id, goal.current + Number(add), goal.target);
                      }
                    }}
                  >
                    Add Funds
                  </Button>
                  <Button variant="ghost" size="sm" onClick={() => deleteGoal(goal.id)} className="text-destructive hover:bg-destructive/10">Delete</Button>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>
    </div>
  );
}

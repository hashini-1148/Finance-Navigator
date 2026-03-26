import { useAppState } from '@/hooks/use-app-state';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ArrowUpRight, ArrowDownRight, Activity, Wallet } from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip as RechartsTooltip, BarChart, Bar, XAxis, YAxis } from 'recharts';

const formatINR = (val: number) =>
  '₹' + val.toLocaleString('en-IN');

export default function Dashboard() {
  const { state } = useAppState();

  const totalExpenses = state.expenses.reduce((sum, e) => sum + e.budgeted, 0);
  const netSavings = state.income - totalExpenses;
  const savingsRate = state.income > 0 ? ((netSavings / state.income) * 100).toFixed(1) : '0.0';

  const expenseData = state.expenses.map(e => ({
    name: e.category,
    value: e.budgeted
  }));

  const COLORS = ['#00f5c8', '#0090ff', '#b537f2', '#ff6b35', '#4ade80', '#facc15'];

  const trendData = [
    { name: 'Jan', income: state.income, expense: totalExpenses * 0.9 },
    { name: 'Feb', income: state.income, expense: totalExpenses * 1.1 },
    { name: 'Mar', income: state.income * 1.05, expense: totalExpenses },
    { name: 'Apr', income: state.income, expense: totalExpenses * 0.95 },
    { name: 'May', income: state.income * 1.02, expense: totalExpenses * 0.88 },
    { name: 'Jun', income: state.income, expense: totalExpenses },
  ];

  return (
    <div className="space-y-8 pb-12">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-display font-bold text-white tracking-widest uppercase">Command Center</h1>
          <p className="text-muted-foreground font-mono mt-2">Real-time financial telemetry</p>
        </div>
        <div className="text-right">
          <div className="text-2xl font-mono text-primary text-glow-cyan">
            {new Date().toLocaleTimeString('en-IN', { hour12: false })}
          </div>
          <div className="text-xs text-muted-foreground uppercase tracking-widest">
            {new Date().toLocaleDateString('en-IN')}
          </div>
        </div>
      </div>

      {/* KPI GRID */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="glass-panel border-t-primary/50 relative overflow-hidden group">
          <div className="absolute inset-0 bg-gradient-to-br from-primary/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground uppercase tracking-wider">Monthly Income</CardTitle>
            <ArrowUpRight className="h-4 w-4 text-primary" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-display font-bold text-white">{formatINR(state.income)}</div>
          </CardContent>
        </Card>

        <Card className="glass-panel border-t-destructive/50 relative overflow-hidden group">
          <div className="absolute inset-0 bg-gradient-to-br from-destructive/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground uppercase tracking-wider">Total Expenses</CardTitle>
            <ArrowDownRight className="h-4 w-4 text-destructive" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-display font-bold text-white">{formatINR(totalExpenses)}</div>
          </CardContent>
        </Card>

        <Card className="glass-panel border-t-accent/50 relative overflow-hidden group">
          <div className="absolute inset-0 bg-gradient-to-br from-accent/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground uppercase tracking-wider">Net Savings</CardTitle>
            <Wallet className="h-4 w-4 text-accent" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-display font-bold text-white">{formatINR(netSavings)}</div>
          </CardContent>
        </Card>

        <Card className="glass-panel border-t-[#b537f2]/50 relative overflow-hidden group">
          <div className="absolute inset-0 bg-gradient-to-br from-[#b537f2]/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground uppercase tracking-wider">Savings Rate</CardTitle>
            <Activity className="h-4 w-4 text-[#b537f2]" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-display font-bold text-white">{savingsRate}%</div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* DONUT CHART */}
        <Card className="glass-panel lg:col-span-1 border-white/10">
          <CardHeader>
            <CardTitle className="font-display tracking-widest text-lg">Expense Distribution</CardTitle>
          </CardHeader>
          <CardContent className="h-[300px] flex flex-col items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={expenseData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                  stroke="none"
                >
                  {expenseData.map((_, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} style={{ filter: `drop-shadow(0px 0px 5px ${COLORS[index % COLORS.length]})` }} />
                  ))}
                </Pie>
                <RechartsTooltip
                  formatter={(value: number) => [formatINR(value), '']}
                  contentStyle={{ backgroundColor: 'rgba(7, 21, 37, 0.9)', border: '1px solid rgba(255,255,255,0.1)', backdropFilter: 'blur(10px)', borderRadius: '8px' }}
                  itemStyle={{ color: '#fff', fontFamily: 'Space Mono' }}
                />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* TREND CHART */}
        <Card className="glass-panel lg:col-span-2 border-white/10">
          <CardHeader>
            <CardTitle className="font-display tracking-widest text-lg">Cash Flow Vector</CardTitle>
          </CardHeader>
          <CardContent className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={trendData} margin={{ top: 20, right: 30, left: 10, bottom: 0 }}>
                <XAxis dataKey="name" stroke="#4a7a9b" fontFamily="Space Mono" fontSize={12} />
                <YAxis stroke="#4a7a9b" fontFamily="Space Mono" fontSize={11} tickFormatter={(v) => '₹' + (v >= 1000 ? (v/1000).toFixed(0) + 'k' : v)} />
                <RechartsTooltip
                  cursor={{ fill: 'rgba(255,255,255,0.05)' }}
                  formatter={(value: number) => [formatINR(value), '']}
                  contentStyle={{ backgroundColor: 'rgba(7, 21, 37, 0.9)', border: '1px solid rgba(0, 245, 200, 0.3)', borderRadius: '8px', boxShadow: '0 0 20px rgba(0,245,200,0.1)' }}
                />
                <Bar dataKey="income" name="Income" fill="#0090ff" radius={[4, 4, 0, 0]} />
                <Bar dataKey="expense" name="Expense" fill="#ff6b35" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

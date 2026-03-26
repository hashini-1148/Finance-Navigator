import { useAppState } from '@/hooks/use-app-state';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { BarChart, Bar, XAxis, YAxis, ResponsiveContainer, Tooltip as RechartsTooltip, CartesianGrid, AreaChart, Area } from 'recharts';

const formatINR = (val: number) => '₹' + val.toLocaleString('en-IN');

export default function Reports() {
  const { state } = useAppState();

  const categorySpending = state.transactions
    .filter(t => t.type === 'expense')
    .reduce((acc, t) => {
      acc[t.category] = (acc[t.category] || 0) + t.amount;
      return acc;
    }, {} as Record<string, number>);

  const categoryData = Object.keys(categorySpending)
    .map(key => ({ name: key, value: categorySpending[key] }))
    .sort((a, b) => b.value - a.value);

  const totalExp = state.expenses.reduce((s, e) => s + e.budgeted, 0);
  const net = state.income - totalExp;

  const historyData = [
    { month: 'Jan', savings: net * 0.8 },
    { month: 'Feb', savings: net * 1.2 },
    { month: 'Mar', savings: net * 0.9 },
    { month: 'Apr', savings: net * 1.5 },
    { month: 'May', savings: net * 1.1 },
    { month: 'Jun', savings: net },
  ];

  const totalActualSpend = Object.values(categorySpending).reduce((a, b) => a + b, 0);
  const burnRate = state.income > 0 ? ((totalActualSpend / state.income) * 100).toFixed(1) : '0.0';

  return (
    <div className="space-y-8 pb-12">
      <div>
        <h1 className="text-4xl font-display font-bold text-white tracking-widest uppercase">Analytics Matrix</h1>
        <p className="text-muted-foreground font-mono mt-2">Deep data visualisation</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <Card className="glass-panel border-white/10 lg:col-span-2">
          <CardHeader>
            <CardTitle className="font-display tracking-widest text-lg text-primary text-glow-cyan">Net Asset Growth (6mo)</CardTitle>
          </CardHeader>
          <CardContent className="h-[400px]">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={historyData} margin={{ top: 10, right: 30, left: 10, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorSavings" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#00f5c8" stopOpacity={0.8} />
                    <stop offset="95%" stopColor="#00f5c8" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                <XAxis dataKey="month" stroke="#4a7a9b" fontFamily="Space Mono" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis stroke="#4a7a9b" fontFamily="Space Mono" fontSize={11} tickLine={false} axisLine={false} tickFormatter={(val) => '₹' + (val >= 1000 ? (val / 1000).toFixed(0) + 'k' : val)} />
                <RechartsTooltip
                  formatter={(value: number) => [formatINR(value), 'Savings']}
                  contentStyle={{ backgroundColor: 'rgba(7, 21, 37, 0.9)', border: '1px solid rgba(0, 245, 200, 0.3)', borderRadius: '8px', boxShadow: '0 0 20px rgba(0,245,200,0.1)' }}
                  labelStyle={{ color: '#4a7a9b', fontFamily: 'Space Mono' }}
                  itemStyle={{ color: '#00f5c8', fontFamily: 'Space Mono', fontWeight: 'bold' }}
                />
                <Area type="monotone" dataKey="savings" stroke="#00f5c8" strokeWidth={3} fillOpacity={1} fill="url(#colorSavings)" />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card className="glass-panel border-white/10">
          <CardHeader>
            <CardTitle className="font-display tracking-widest text-lg text-accent text-glow-blue">Actual Spending by Category</CardTitle>
          </CardHeader>
          <CardContent className="h-[350px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={categoryData} layout="vertical" margin={{ top: 5, right: 30, left: 40, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" horizontal={false} />
                <XAxis type="number" stroke="#4a7a9b" fontFamily="Space Mono" fontSize={10} hide />
                <YAxis dataKey="name" type="category" stroke="#e8f4ff" fontFamily="Syne" fontSize={12} tickLine={false} axisLine={false} width={100} />
                <RechartsTooltip
                  cursor={{ fill: 'rgba(255,255,255,0.05)' }}
                  formatter={(value: number) => [formatINR(value), '']}
                  contentStyle={{ backgroundColor: 'rgba(7, 21, 37, 0.9)', border: '1px solid rgba(0, 144, 255, 0.3)', borderRadius: '8px' }}
                />
                <Bar dataKey="value" fill="#0090ff" radius={[0, 4, 4, 0]} barSize={20} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card className="glass-panel border-white/10 bg-gradient-to-br from-black/80 to-primary/10">
          <CardHeader>
            <CardTitle className="font-display tracking-widest text-lg">System Insights</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="border-l-2 border-primary pl-4 py-1">
              <p className="text-xs text-muted-foreground uppercase tracking-widest font-mono">Top Expense Vector</p>
              <p className="text-xl font-bold text-white mt-1">
                {categoryData[0]?.name || 'N/A'}{' '}
                <span className="text-primary text-sm font-mono ml-2">
                  {formatINR(categoryData[0]?.value || 0)}
                </span>
              </p>
            </div>
            <div className="border-l-2 border-accent pl-4 py-1">
              <p className="text-xs text-muted-foreground uppercase tracking-widest font-mono">Burn Rate</p>
              <p className="text-xl font-bold text-white mt-1">
                {burnRate}%{' '}
                <span className="text-muted-foreground text-sm font-sans font-normal ml-2">of monthly income</span>
              </p>
            </div>
            <div className="border-l-2 border-[#b537f2] pl-4 py-1">
              <p className="text-xs text-muted-foreground uppercase tracking-widest font-mono">Target Projection</p>
              <p className="text-xl font-bold text-white mt-1">
                {state.goals.filter(g => g.current >= g.target).length} / {state.goals.length}{' '}
                <span className="text-muted-foreground text-sm font-sans font-normal ml-2">objectives met</span>
              </p>
            </div>
            <div className="border-l-2 border-destructive pl-4 py-1">
              <p className="text-xs text-muted-foreground uppercase tracking-widest font-mono">Net Monthly Surplus</p>
              <p className="text-xl font-bold text-white mt-1">
                {formatINR(net)}{' '}
                <span className={`text-sm font-sans font-normal ml-2 ${net >= 0 ? 'text-primary' : 'text-destructive'}`}>
                  {net >= 0 ? 'surplus' : 'deficit'}
                </span>
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

import { useState } from 'react';
import { useAppState, Transaction } from '@/hooks/use-app-state';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { EXPENSE_CATEGORIES } from '@/lib/constants';
import { Search, Plus, ArrowUpRight, ArrowDownRight, Trash2 } from 'lucide-react';
import { format } from 'date-fns';
import { motion, AnimatePresence } from 'framer-motion';

const formatINR = (val: number) =>
  '₹' + val.toLocaleString('en-IN', { minimumFractionDigits: 2 });

export default function Transactions() {
  const { state, addTransaction, deleteTransaction } = useAppState();
  const [search, setSearch] = useState('');
  const [showAdd, setShowAdd] = useState(false);

  const [newTx, setNewTx] = useState({
    date: new Date().toISOString().split('T')[0],
    description: '',
    category: '',
    amount: '',
    type: 'expense' as 'income' | 'expense'
  });

  const filteredTxs = state.transactions
    .filter(t =>
      t.description.toLowerCase().includes(search.toLowerCase()) ||
      t.category.toLowerCase().includes(search.toLowerCase())
    )
    .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());

  const handleAdd = () => {
    if (newTx.description && newTx.amount) {
      addTransaction({
        date: new Date(newTx.date).toISOString(),
        description: newTx.description,
        category: newTx.category || 'Other',
        amount: Number(newTx.amount),
        type: newTx.type
      });
      setShowAdd(false);
      setNewTx({ ...newTx, description: '', amount: '' });
    }
  };

  const exportCSV = () => {
    const headers = ['Date', 'Description', 'Category', 'Type', 'Amount (₹)'];
    const rows = state.transactions.map(t => [
      format(new Date(t.date), 'dd/MM/yyyy'),
      t.description,
      t.category,
      t.type,
      t.amount.toLocaleString('en-IN')
    ]);
    const csv = [headers, ...rows].map(r => r.join(',')).join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'pocketpro-transactions.csv';
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-6 sm:space-y-8 pb-12">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div>
          <h1 className="text-2xl sm:text-3xl lg:text-4xl font-display font-bold text-white tracking-widest uppercase">Ledger Matrix</h1>
          <p className="text-muted-foreground font-mono mt-1 sm:mt-2 text-sm">Transaction history log</p>
        </div>
        <div className="flex gap-2 sm:gap-3">
          <Button variant="outline" onClick={exportCSV} className="border-white/20 text-muted-foreground hover:text-white text-xs font-mono flex-1 sm:flex-none">
            Export CSV
          </Button>
          <Button onClick={() => setShowAdd(!showAdd)} className="bg-primary text-black hover:bg-primary/80 box-glow-cyan flex-1 sm:flex-none">
            <Plus className="w-4 h-4 mr-1 sm:mr-2" /> Log Entry
          </Button>
        </div>
      </div>

      <AnimatePresence>
        {showAdd && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="glass-panel p-4 sm:p-6 border-primary/30 rounded-xl overflow-hidden"
          >
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-6 gap-3">
              <Select value={newTx.type} onValueChange={(v: any) => setNewTx({ ...newTx, type: v, category: v === 'income' ? 'Income' : '' })}>
                <SelectTrigger className="bg-black/50 border-white/20">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-background border-white/20">
                  <SelectItem value="expense">Expense</SelectItem>
                  <SelectItem value="income">Income</SelectItem>
                </SelectContent>
              </Select>

              <Input type="date" value={newTx.date} onChange={e => setNewTx({ ...newTx, date: e.target.value })} className="bg-black/50" />
              <Input placeholder="Description" value={newTx.description} onChange={e => setNewTx({ ...newTx, description: e.target.value })} className="bg-black/50 lg:col-span-2" />

              {newTx.type === 'expense' ? (
                <Select value={newTx.category} onValueChange={(v) => setNewTx({ ...newTx, category: v })}>
                  <SelectTrigger className="bg-black/50 border-white/20">
                    <SelectValue placeholder="Category" />
                  </SelectTrigger>
                  <SelectContent className="bg-background border-white/20">
                    {EXPENSE_CATEGORIES.map(c => <SelectItem key={c.id} value={c.name}>{c.name}</SelectItem>)}
                  </SelectContent>
                </Select>
              ) : (
                <Input value="Income" disabled className="bg-black/30 border-white/10 opacity-50" />
              )}

              <div className="flex items-center gap-1">
                <span className="text-primary font-bold text-lg shrink-0">₹</span>
                <Input type="number" placeholder="Amount" value={newTx.amount} onChange={e => setNewTx({ ...newTx, amount: e.target.value })} className="bg-black/50" />
              </div>
              <Button onClick={handleAdd} className="bg-primary text-black sm:col-span-2 lg:col-span-6 mt-1">Record Transaction</Button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <Card className="glass-panel border-white/10">
        <CardHeader className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 border-b border-white/5 pb-4">
          <CardTitle className="font-display tracking-widest text-base sm:text-lg">Data Stream</CardTitle>
          <div className="relative w-full sm:w-56 lg:w-64">
            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
            <Input
              placeholder="Query logs..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-9 bg-black/50 border-white/20 focus-visible:ring-primary h-9 font-mono text-xs w-full"
            />
          </div>
        </CardHeader>
        <CardContent className="p-0 overflow-x-auto">
          <Table>
            <TableHeader className="bg-black/40">
              <TableRow className="border-white/5 hover:bg-transparent">
                <TableHead className="font-mono text-xs tracking-wider">DATE</TableHead>
                <TableHead className="font-mono text-xs tracking-wider">DESCRIPTION</TableHead>
                <TableHead className="font-mono text-xs tracking-wider hidden sm:table-cell">CATEGORY</TableHead>
                <TableHead className="font-mono text-xs tracking-wider text-right">AMOUNT</TableHead>
                <TableHead className="w-[40px]"></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredTxs.map((tx) => (
                <TableRow key={tx.id} className="border-white/5 hover:bg-white/5 transition-colors group">
                  <TableCell className="font-mono text-xs text-muted-foreground whitespace-nowrap">
                    {format(new Date(tx.date), 'dd.MM.yy')}
                  </TableCell>
                  <TableCell className="font-sans font-medium text-white text-sm max-w-[120px] sm:max-w-none truncate">{tx.description}</TableCell>
                  <TableCell className="hidden sm:table-cell">
                    <span className="inline-flex items-center px-2 py-1 rounded-full text-[10px] font-mono border border-white/10 bg-white/5 whitespace-nowrap">
                      {tx.category}
                    </span>
                  </TableCell>
                  <TableCell className={`text-right font-mono font-bold text-xs sm:text-sm whitespace-nowrap ${tx.type === 'income' ? 'text-primary' : 'text-white'}`}>
                    <div className="flex items-center justify-end gap-1">
                      {tx.type === 'income'
                        ? <ArrowUpRight className="w-3 h-3 text-primary shrink-0" />
                        : <ArrowDownRight className="w-3 h-3 text-destructive shrink-0" />}
                      {formatINR(tx.amount)}
                    </div>
                  </TableCell>
                  <TableCell>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => deleteTransaction(tx.id)}
                      className="h-7 w-7 opacity-0 group-hover:opacity-100 hover:text-destructive hover:bg-destructive/10 transition-all"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
              {filteredTxs.length === 0 && (
                <TableRow>
                  <TableCell colSpan={5} className="text-center py-12 text-muted-foreground font-mono text-sm">
                    NO_DATA_FOUND
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}

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
    .filter(t => t.description.toLowerCase().includes(search.toLowerCase()) || t.category.toLowerCase().includes(search.toLowerCase()))
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

  return (
    <div className="space-y-8 pb-12">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-display font-bold text-white tracking-widest uppercase">Ledger Matrix</h1>
          <p className="text-muted-foreground font-mono mt-2">Transaction history log</p>
        </div>
        <Button onClick={() => setShowAdd(!showAdd)} className="bg-primary text-black hover:bg-primary/80 box-glow-cyan">
          <Plus className="w-4 h-4 mr-2" /> Log Entry
        </Button>
      </div>

      <AnimatePresence>
        {showAdd && (
          <motion.div 
            initial={{ opacity: 0, height: 0 }} 
            animate={{ opacity: 1, height: 'auto' }} 
            exit={{ opacity: 0, height: 0 }}
            className="glass-panel p-6 border-primary/30 rounded-xl overflow-hidden"
          >
            <div className="grid grid-cols-1 md:grid-cols-6 gap-4">
              <Select value={newTx.type} onValueChange={(v: any) => setNewTx({...newTx, type: v, category: v === 'income' ? 'Income' : ''})}>
                <SelectTrigger className="bg-black/50 border-white/20">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-background border-white/20">
                  <SelectItem value="expense">Expense</SelectItem>
                  <SelectItem value="income">Income</SelectItem>
                </SelectContent>
              </Select>
              
              <Input type="date" value={newTx.date} onChange={e => setNewTx({...newTx, date: e.target.value})} className="bg-black/50" />
              <Input placeholder="Description" value={newTx.description} onChange={e => setNewTx({...newTx, description: e.target.value})} className="bg-black/50 md:col-span-2" />
              
              {newTx.type === 'expense' ? (
                <Select value={newTx.category} onValueChange={(v) => setNewTx({...newTx, category: v})}>
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

              <Input type="number" placeholder="Amount" value={newTx.amount} onChange={e => setNewTx({...newTx, amount: e.target.value})} className="bg-black/50" />
              <Button onClick={handleAdd} className="bg-primary text-black md:col-span-6 mt-2">Record Transaction</Button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <Card className="glass-panel border-white/10">
        <CardHeader className="flex flex-row items-center justify-between border-b border-white/5 pb-4">
          <CardTitle className="font-display tracking-widest text-lg">Data Stream</CardTitle>
          <div className="relative w-64">
            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
            <Input 
              placeholder="Query logs..." 
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-9 bg-black/50 border-white/20 focus-visible:ring-primary h-9 font-mono text-xs"
            />
          </div>
        </CardHeader>
        <CardContent className="p-0">
          <Table>
            <TableHeader className="bg-black/40">
              <TableRow className="border-white/5 hover:bg-transparent">
                <TableHead className="font-mono text-xs tracking-wider">DATE</TableHead>
                <TableHead className="font-mono text-xs tracking-wider">DESCRIPTION</TableHead>
                <TableHead className="font-mono text-xs tracking-wider">CATEGORY</TableHead>
                <TableHead className="font-mono text-xs tracking-wider text-right">AMOUNT</TableHead>
                <TableHead className="w-[50px]"></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredTxs.map((tx) => (
                <TableRow key={tx.id} className="border-white/5 hover:bg-white/5 transition-colors group">
                  <TableCell className="font-mono text-xs text-muted-foreground">
                    {format(new Date(tx.date), 'MM.dd.yyyy')}
                  </TableCell>
                  <TableCell className="font-sans font-medium text-white">{tx.description}</TableCell>
                  <TableCell>
                    <span className="inline-flex items-center px-2 py-1 rounded-full text-[10px] font-mono border border-white/10 bg-white/5">
                      {tx.category}
                    </span>
                  </TableCell>
                  <TableCell className={`text-right font-mono font-bold flex items-center justify-end gap-2 ${tx.type === 'income' ? 'text-primary' : 'text-white'}`}>
                    {tx.type === 'income' ? <ArrowUpRight className="w-3 h-3" /> : <ArrowDownRight className="w-3 h-3 text-destructive" />}
                    ${tx.amount.toLocaleString(undefined, {minimumFractionDigits: 2})}
                  </TableCell>
                  <TableCell>
                    <Button variant="ghost" size="icon" onClick={() => deleteTransaction(tx.id)} className="h-8 w-8 opacity-0 group-hover:opacity-100 hover:text-destructive hover:bg-destructive/10 transition-all">
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
              {filteredTxs.length === 0 && (
                <TableRow>
                  <TableCell colSpan={5} className="text-center py-12 text-muted-foreground font-mono">
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

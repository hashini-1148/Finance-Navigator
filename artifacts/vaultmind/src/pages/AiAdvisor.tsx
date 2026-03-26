import { useState, useRef, useEffect } from 'react';
import { useAppState } from '@/hooks/use-app-state';
import { useOpenRouter } from '@/hooks/use-open-router';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { AI_MODELS } from '@/lib/constants';
import { Send, Sparkles, Brain, Loader2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import ReactMarkdown from 'react-markdown';

type Message = { role: 'user' | 'assistant'; content: string };

export default function AiAdvisor() {
  const { state, updateSettings } = useAppState();
  const { askAi, isPending, error } = useOpenRouter();
  const [messages, setMessages] = useState<Message[]>([
    { role: 'assistant', content: "Greetings. I am VaultMind AI. My neural nets are connected to your local telemetry. How may I optimize your financial vectors today?" }
  ]);
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isPending]);

  const handleSend = async (text: string) => {
    if (!text.trim()) return;
    
    const userMsg: Message = { role: 'user', content: text };
    setMessages(prev => [...prev, userMsg]);
    setInput('');

    try {
      // Map local messages to OpenRouter expected format
      const history = messages.map(m => ({ role: m.role, content: m.content }));
      const response = await askAi(text, history);
      
      setMessages(prev => [...prev, { role: 'assistant', content: response }]);
    } catch (err) {
      // Error handled by hook, toast could be added
    }
  };

  const handleFullAnalysis = async () => {
    handleSend("Please run a full diagnostic on my financial telemetry and provide the standard 5-point assessment.");
  };

  const QUICK_QUESTIONS = [
    "How can I save more?",
    "Analyze my spending",
    "Debt payoff plan",
    "Is my 50/30/20 healthy?"
  ];

  return (
    <div className="h-[calc(100vh-8rem)] flex flex-col pb-6">
      <div className="flex items-center justify-between mb-6 shrink-0">
        <div>
          <h1 className="text-4xl font-display font-bold text-white tracking-widest uppercase flex items-center gap-3">
            <Brain className="w-8 h-8 text-[#b537f2] animate-pulse" />
            Neural Advisor
          </h1>
          <p className="text-muted-foreground font-mono mt-2">Advanced cognitive financial analysis</p>
        </div>
        
        <div className="flex items-center gap-4">
          <Button onClick={handleFullAnalysis} className="bg-[#b537f2]/20 text-[#b537f2] hover:bg-[#b537f2]/30 border border-[#b537f2]/50 shadow-[0_0_15px_rgba(181,55,242,0.2)]">
            <Sparkles className="w-4 h-4 mr-2" /> Full Diagnostic
          </Button>
          <Select 
            value={state.settings.selectedModel} 
            onValueChange={(v) => updateSettings({ selectedModel: v })}
          >
            <SelectTrigger className="w-[200px] bg-black/50 border-white/20 font-mono text-xs">
              <SelectValue placeholder="Select Neural Core" />
            </SelectTrigger>
            <SelectContent className="bg-background border-white/20">
              {AI_MODELS.map(model => (
                <SelectItem key={model.id} value={model.id} className="font-mono text-xs focus:bg-white/10">
                  {model.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      {error && (
        <div className="bg-destructive/20 border border-destructive/50 text-destructive px-4 py-2 rounded-lg mb-4 text-sm font-mono shrink-0">
          SYS.ERR: {error}
        </div>
      )}

      <Card className="flex-1 glass-panel border-white/10 flex flex-col overflow-hidden relative">
        <div className="flex-1 overflow-y-auto p-6 space-y-6 scroll-smooth">
          <AnimatePresence initial={false}>
            {messages.map((msg, idx) => (
              <motion.div 
                key={idx}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div className={`max-w-[80%] rounded-2xl p-4 ${
                  msg.role === 'user' 
                    ? 'bg-accent/20 border border-accent/30 text-white rounded-br-none shadow-[0_0_15px_rgba(0,144,255,0.1)]' 
                    : 'bg-black/60 border border-primary/20 text-foreground rounded-bl-none shadow-[0_0_15px_rgba(0,245,200,0.05)] prose prose-invert max-w-none prose-p:leading-relaxed prose-pre:bg-black/50 prose-pre:border prose-pre:border-white/10'
                }`}>
                  {msg.role === 'assistant' ? (
                    <ReactMarkdown>{msg.content}</ReactMarkdown>
                  ) : (
                    <p className="font-sans text-sm">{msg.content}</p>
                  )}
                </div>
              </motion.div>
            ))}
            {isPending && (
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex justify-start">
                <div className="bg-black/60 border border-primary/20 rounded-2xl rounded-bl-none p-4 flex items-center gap-2">
                  <Loader2 className="w-4 h-4 text-primary animate-spin" />
                  <span className="text-xs font-mono text-primary animate-pulse">PROCESSING_</span>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
          <div ref={messagesEndRef} />
        </div>

        <div className="p-4 border-t border-white/10 bg-black/40">
          <div className="flex flex-wrap gap-2 mb-4">
            {QUICK_QUESTIONS.map(q => (
              <button 
                key={q}
                onClick={() => handleSend(q)}
                className="text-xs font-mono px-3 py-1.5 rounded-full border border-white/10 text-muted-foreground hover:text-white hover:border-primary/50 transition-colors"
              >
                {q}
              </button>
            ))}
          </div>
          <form 
            onSubmit={(e) => { e.preventDefault(); handleSend(input); }}
            className="flex gap-4 relative"
          >
            <div className="absolute inset-0 bg-primary/5 rounded-xl pointer-events-none blur-md" />
            <Input 
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Input query parameters..." 
              className="bg-black/80 border-primary/30 h-14 font-sans text-base focus-visible:ring-primary focus-visible:ring-offset-0 relative z-10"
              disabled={isPending}
            />
            <Button 
              type="submit" 
              disabled={isPending || !input.trim()} 
              className="h-14 w-14 bg-primary text-black hover:bg-primary/80 relative z-10 box-glow-cyan"
            >
              <Send className="w-5 h-5" />
            </Button>
          </form>
        </div>
      </Card>
    </div>
  );
}

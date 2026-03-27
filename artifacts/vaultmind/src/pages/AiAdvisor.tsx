import { useState, useRef, useEffect } from 'react';
import { useAppState } from '@/hooks/use-app-state';
import { useOpenRouter } from '@/hooks/use-open-router';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { AI_MODELS } from '@/lib/constants';
import { Send, Sparkles, Brain, Loader2, Key } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import ReactMarkdown from 'react-markdown';
import { useLocation } from 'wouter';

type Message = { role: 'user' | 'assistant'; content: string };

export default function AiAdvisor() {
  const { state, updateSettings } = useAppState();
  const { askAi, isPending, error, isKeyInvalid } = useOpenRouter();
  const [, setLocation] = useLocation();
  const [messages, setMessages] = useState<Message[]>([
    { role: 'assistant', content: "Namaste! I'm PocketPro AI, powered by Google Gemini. My neural nets are connected to your financial data. Ask me anything about your budget, savings, SIPs, or taxes — I'll give you personalised Indian finance advice! 🇮🇳" }
  ]);
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isPending]);

  const handleSend = async (text: string) => {
    if (!text.trim()) return;
    const userMsg: Message = { role: 'user', content: text };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    try {
      const history = messages.map(m => ({ role: m.role, content: m.content }));
      const response = await askAi(text, history);
      setMessages(prev => [...prev, { role: 'assistant', content: response }]);
    } catch (_) {}
  };

  const handleFullAnalysis = () => {
    handleSend("Please run a complete analysis of my finances and provide a detailed 5-point assessment with specific Indian savings recommendations.");
  };

  const QUICK_QUESTIONS = [
    "How can I save more this month?",
    "Analyse my spending patterns",
    "Best SIP strategy for me?",
    "Is my 50/30/20 budget healthy?",
    "How to maximise 80C deductions?",
    "Emergency fund advice",
  ];

  const noApiKey = isKeyInvalid;

  return (
    <div className="h-[calc(100vh-8rem)] flex flex-col pb-6">
      <div className="flex items-center justify-between mb-6 shrink-0 flex-wrap gap-4">
        <div>
          <h1 className="text-4xl font-display font-bold text-white tracking-widest uppercase flex items-center gap-3">
            <Brain className="w-8 h-8 text-[#b537f2] animate-pulse" />
            Gemini Advisor
          </h1>
          <p className="text-muted-foreground font-mono mt-1 text-sm">Powered by Google AI Studio · Indian Finance Expert</p>
        </div>

        <div className="flex items-center gap-3 flex-wrap">
          <Button onClick={handleFullAnalysis} disabled={isPending || noApiKey} className="bg-[#b537f2]/20 text-[#b537f2] hover:bg-[#b537f2]/30 border border-[#b537f2]/50 shadow-[0_0_15px_rgba(181,55,242,0.2)]">
            <Sparkles className="w-4 h-4 mr-2" /> Full Diagnostic
          </Button>
          <Select
            value={state.settings.selectedModel}
            onValueChange={(v) => updateSettings({ selectedModel: v })}
          >
            <SelectTrigger className="w-[200px] bg-black/50 border-white/20 font-mono text-xs">
              <SelectValue placeholder="Select Gemini Model" />
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

      {noApiKey && (
        <div className="bg-yellow-500/10 border border-yellow-500/40 text-yellow-300 px-4 py-3 rounded-xl mb-4 text-sm font-sans flex items-center gap-3 shrink-0">
          <Key className="w-4 h-4 shrink-0" />
          <span>
            Add your <strong>Google AI Studio API key</strong> to start chatting.{' '}
            <button
              className="underline text-primary hover:text-primary/80 ml-1"
              onClick={() => {
                const btn = document.querySelector('[data-set-key]') as HTMLButtonElement;
                btn?.click();
                // Fallback: click the header key button
                const headerBtn = Array.from(document.querySelectorAll('button')).find(b => b.textContent?.includes('Gemini Key') || b.textContent?.includes('Set Gemini Key'));
                headerBtn?.click();
              }}
            >
              Click "Set Gemini Key" in the top-right to get started.
            </button>
          </span>
        </div>
      )}

      {error && (
        <div className="bg-destructive/20 border border-destructive/50 text-destructive px-4 py-3 rounded-xl mb-4 text-sm font-mono shrink-0">
          ⚠ {error}
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
                {msg.role === 'assistant' && (
                  <div className="w-8 h-8 rounded-full bg-[#b537f2]/20 border border-[#b537f2]/40 flex items-center justify-center mr-3 mt-1 shrink-0">
                    <Brain className="w-4 h-4 text-[#b537f2]" />
                  </div>
                )}
                <div className={`max-w-[78%] rounded-2xl p-4 text-sm ${
                  msg.role === 'user'
                    ? 'bg-accent/20 border border-accent/30 text-white rounded-br-none shadow-[0_0_15px_rgba(0,144,255,0.1)]'
                    : 'bg-black/60 border border-primary/20 text-foreground rounded-bl-none shadow-[0_0_15px_rgba(0,245,200,0.05)] prose prose-invert max-w-none prose-p:leading-relaxed prose-pre:bg-black/50 prose-pre:border prose-pre:border-white/10 prose-sm'
                }`}>
                  {msg.role === 'assistant' ? (
                    <ReactMarkdown>{msg.content}</ReactMarkdown>
                  ) : (
                    <p className="font-sans">{msg.content}</p>
                  )}
                </div>
              </motion.div>
            ))}
            {isPending && (
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex justify-start items-center gap-3">
                <div className="w-8 h-8 rounded-full bg-[#b537f2]/20 border border-[#b537f2]/40 flex items-center justify-center shrink-0">
                  <Brain className="w-4 h-4 text-[#b537f2]" />
                </div>
                <div className="bg-black/60 border border-primary/20 rounded-2xl rounded-bl-none px-5 py-4 flex items-center gap-3">
                  <Loader2 className="w-4 h-4 text-primary animate-spin" />
                  <span className="text-xs font-mono text-primary animate-pulse">GEMINI PROCESSING_</span>
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
                disabled={isPending || noApiKey}
                className="text-xs font-mono px-3 py-1.5 rounded-full border border-white/10 text-muted-foreground hover:text-white hover:border-primary/50 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
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
              placeholder={noApiKey ? "Add your Gemini API key to start..." : "Ask PocketPro AI anything about your finances..."}
              className="bg-black/80 border-primary/30 h-14 font-sans text-base focus-visible:ring-primary focus-visible:ring-offset-0 relative z-10"
              disabled={isPending || noApiKey}
            />
            <Button
              type="submit"
              disabled={isPending || !input.trim() || noApiKey}
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

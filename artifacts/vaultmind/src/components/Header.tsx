import { useState } from 'react';
import { useAppState } from '@/hooks/use-app-state';
import { Key, Eye, EyeOff, Save, Trash2, Download } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DialogDescription,
} from "@/components/ui/dialog";

export function Header() {
  const { state, updateSettings, resetData } = useAppState();
  const [showKey, setShowKey] = useState(false);
  const [keyInput, setKeyInput] = useState(state.settings.apiKey);
  const { toast } = useToast();

  const handleSaveKey = () => {
    updateSettings({ apiKey: keyInput });
    toast({ title: "Gemini API Key Saved", description: "Stored securely in your browser." });
  };

  const handleExport = () => {
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(state));
    const a = document.createElement('a');
    a.setAttribute("href", dataStr);
    a.setAttribute("download", "pocketpro_backup.json");
    document.body.appendChild(a);
    a.click();
    a.remove();
    toast({ title: "Data Exported", description: "Your local data has been downloaded." });
  };

  return (
    <header className="h-20 border-b border-white/10 bg-background/40 backdrop-blur-md flex items-center justify-between px-8 sticky top-0 z-40">
      <div>
        <h2 className="text-xl font-display font-bold text-foreground tracking-widest flex items-center gap-3">
          <span className="w-2 h-2 rounded-full bg-primary animate-pulse shadow-[0_0_10px_#00f5c8]"></span>
          SYS.OP.MODE
        </h2>
      </div>

      <div className="flex items-center gap-4">
        <Dialog>
          <DialogTrigger asChild>
            <Button variant="outline" className="glass-panel border-primary/30 text-primary hover:bg-primary/10 transition-all">
              <Key className="w-4 h-4 mr-2" />
              {state.settings.apiKey ? 'Gemini Key ✓' : 'Set Gemini Key'}
            </Button>
          </DialogTrigger>
          <DialogContent className="glass-panel border-primary/30 sm:max-w-lg">
            <DialogHeader>
              <DialogTitle className="font-display text-primary flex items-center gap-2">
                <span>Google AI Studio API Key</span>
              </DialogTitle>
              <DialogDescription className="text-muted-foreground text-sm">
                PocketPro uses Gemini (Google AI Studio) for AI analysis. Your key is stored only in your local browser — never sent to our servers.
              </DialogDescription>
            </DialogHeader>

            <div className="flex items-center space-x-2 mt-4">
              <div className="relative flex-1">
                <Input
                  type={showKey ? "text" : "password"}
                  value={keyInput}
                  onChange={(e) => setKeyInput(e.target.value)}
                  className="bg-black/50 border-white/20 focus-visible:ring-primary pr-10 font-mono text-sm"
                  placeholder="AIza..."
                />
                <button
                  onClick={() => setShowKey(!showKey)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-white"
                >
                  {showKey ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
              <Button onClick={handleSaveKey} className="bg-primary text-primary-foreground hover:bg-primary/80">
                <Save className="w-4 h-4 mr-2" /> Save
              </Button>
            </div>

            <div className="mt-4 p-3 rounded-lg bg-white/5 border border-white/10 text-xs text-muted-foreground space-y-2">
              <p className="text-white font-medium">How to get your free API key:</p>
              <ol className="list-decimal list-inside space-y-1">
                <li>Go to <a href="https://aistudio.google.com/app/apikey" target="_blank" rel="noreferrer" className="text-primary hover:underline">aistudio.google.com/app/apikey</a></li>
                <li>Sign in with your Google account</li>
                <li>Click <strong>"Create API Key"</strong></li>
                <li>Copy and paste it above</li>
              </ol>
              <p className="text-yellow-400/80">✓ Free tier includes Gemini 2.0 Flash, 1.5 Flash and more — no credit card needed.</p>
            </div>
          </DialogContent>
        </Dialog>

        <Dialog>
          <DialogTrigger asChild>
            <Button variant="ghost" size="icon" className="hover:bg-white/10 rounded-full">
              <Download className="w-5 h-5 text-muted-foreground hover:text-white" />
            </Button>
          </DialogTrigger>
          <DialogContent className="glass-panel border-white/20">
            <DialogHeader>
              <DialogTitle>Data Management</DialogTitle>
              <DialogDescription>Manage your local PocketPro data.</DialogDescription>
            </DialogHeader>
            <div className="flex flex-col gap-4 mt-4">
              <Button onClick={handleExport} variant="outline" className="w-full justify-start border-white/20 hover:bg-white/10">
                <Download className="w-4 h-4 mr-2" /> Backup Data (JSON)
              </Button>
              <Button
                onClick={() => {
                  if (confirm('Reset all data? This cannot be undone.')) {
                    resetData();
                    toast({ title: "Data Reset", variant: "destructive" });
                  }
                }}
                variant="outline"
                className="w-full justify-start border-destructive/50 text-destructive hover:bg-destructive/10"
              >
                <Trash2 className="w-4 h-4 mr-2" /> Reset All Data
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>
    </header>
  );
}

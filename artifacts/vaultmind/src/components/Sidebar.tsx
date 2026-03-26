import { Link, useLocation } from 'wouter';
import { LayoutDashboard, Wallet, Target, BrainCircuit, Receipt, LineChart } from 'lucide-react';
import { clsx } from 'clsx';

const NAV_ITEMS = [
  { href: '/', label: 'Dashboard', icon: LayoutDashboard },
  { href: '/budget', label: 'Budget Planner', icon: Wallet },
  { href: '/goals', label: 'Savings Goals', icon: Target },
  { href: '/ai-advisor', label: 'AI Advisor', icon: BrainCircuit },
  { href: '/transactions', label: 'Transactions', icon: Receipt },
  { href: '/reports', label: 'Reports', icon: LineChart },
];

export function Sidebar() {
  const [location] = useLocation();

  return (
    <aside className="w-[260px] h-screen fixed left-0 top-0 border-r border-white/10 bg-background/60 backdrop-blur-xl flex flex-col z-50">
      <div className="h-20 flex items-center px-6 border-b border-white/10 gap-3">
        <img
          src="/pocketpro-logo.jpeg"
          alt="PocketPro Logo"
          className="w-10 h-10 rounded-xl object-cover shadow-[0_0_12px_rgba(0,245,200,0.3)]"
        />
        <h1 className="text-2xl font-display font-black tracking-widest text-transparent bg-clip-text bg-gradient-to-r from-primary to-accent text-glow-cyan">
          POCKETPRO
        </h1>
      </div>

      <nav className="flex-1 py-8 px-4 flex flex-col gap-2">
        {NAV_ITEMS.map((item) => {
          const isActive = location === item.href;
          const Icon = item.icon;
          return (
            <Link key={item.href} href={item.href}>
              <div
                className={clsx(
                  "flex items-center gap-4 px-4 py-3 rounded-xl transition-all duration-300 group cursor-pointer relative overflow-hidden",
                  isActive
                    ? "bg-primary/10 text-primary border border-primary/30 shadow-[0_0_15px_rgba(0,245,200,0.1)]"
                    : "text-muted-foreground hover:text-foreground hover:bg-white/5 border border-transparent"
                )}
              >
                {isActive && (
                  <div className="absolute left-0 top-0 w-1 h-full bg-primary shadow-[0_0_10px_#00f5c8]" />
                )}
                <Icon className={clsx("w-5 h-5 transition-transform group-hover:scale-110", isActive && "text-glow-cyan")} />
                <span className="font-sans font-medium tracking-wide">{item.label}</span>
              </div>
            </Link>
          );
        })}
      </nav>

      <div className="p-6 border-t border-white/10">
        <div className="glass-panel p-4 rounded-xl flex items-center gap-3">
          <div className="w-3 h-3 rounded-full bg-primary animate-pulse shadow-[0_0_8px_#00f5c8]" />
          <div>
            <p className="text-xs font-mono text-muted-foreground uppercase tracking-wider">System Status</p>
            <p className="text-sm font-semibold text-primary">ONLINE_</p>
          </div>
        </div>
      </div>
    </aside>
  );
}

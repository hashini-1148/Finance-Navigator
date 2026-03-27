import { Link, useLocation } from 'wouter';
import { LayoutDashboard, Wallet, Target, BrainCircuit, Receipt, LineChart, X } from 'lucide-react';
import { clsx } from 'clsx';

const NAV_ITEMS = [
  { href: '/', label: 'Dashboard', icon: LayoutDashboard },
  { href: '/budget', label: 'Budget Planner', icon: Wallet },
  { href: '/goals', label: 'Savings Goals', icon: Target },
  { href: '/ai-advisor', label: 'AI Advisor', icon: BrainCircuit },
  { href: '/transactions', label: 'Transactions', icon: Receipt },
  { href: '/reports', label: 'Reports', icon: LineChart },
];

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

export function Sidebar({ isOpen, onClose }: SidebarProps) {
  const [location] = useLocation();

  return (
    <aside
      className={clsx(
        "w-[260px] h-screen fixed left-0 top-0 border-r border-white/10 bg-background/95 backdrop-blur-xl flex flex-col z-50 transition-transform duration-300",
        "md:translate-x-0",
        isOpen ? "translate-x-0" : "-translate-x-full"
      )}
    >
      <div className="h-16 sm:h-20 flex items-center px-4 sm:px-6 border-b border-white/10 gap-3">
        <img
          src="/pocketpro-logo.jpeg"
          alt="PocketPro Logo"
          className="w-9 h-9 sm:w-10 sm:h-10 rounded-xl object-cover shadow-[0_0_12px_rgba(0,245,200,0.3)]"
        />
        <h1 className="text-xl sm:text-2xl font-display font-black tracking-widest text-transparent bg-clip-text bg-gradient-to-r from-primary to-accent text-glow-cyan">
          POCKETPRO
        </h1>
        <button
          onClick={onClose}
          className="ml-auto text-muted-foreground hover:text-white md:hidden"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      <nav className="flex-1 py-6 px-3 sm:px-4 flex flex-col gap-1.5">
        {NAV_ITEMS.map((item) => {
          const isActive = location === item.href;
          const Icon = item.icon;
          return (
            <Link key={item.href} href={item.href} onClick={onClose}>
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

      <div className="p-4 sm:p-6 border-t border-white/10">
        <div className="glass-panel p-3 sm:p-4 rounded-xl flex items-center gap-3">
          <div className="w-3 h-3 rounded-full bg-primary animate-pulse shadow-[0_0_8px_#00f5c8] shrink-0" />
          <div>
            <p className="text-xs font-mono text-muted-foreground uppercase tracking-wider">System Status</p>
            <p className="text-sm font-semibold text-primary">ONLINE_</p>
          </div>
        </div>
      </div>
    </aside>
  );
}

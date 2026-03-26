import { ReactNode } from 'react';
import { Sidebar } from './Sidebar';
import { Header } from './Header';
import { ThreeBackground } from './ThreeBackground';
import { CustomCursor } from './CustomCursor';
import { motion, AnimatePresence } from 'framer-motion';
import { useLocation } from 'wouter';

export function Layout({ children }: { children: ReactNode }) {
  const [location] = useLocation();

  return (
    <div className="min-h-screen text-foreground overflow-hidden selection:bg-primary/30">
      <CustomCursor />
      <ThreeBackground />
      <Sidebar />
      <main className="ml-[260px] flex flex-col min-h-screen">
        <Header />
        <div className="flex-1 p-8 overflow-y-auto relative">
          <AnimatePresence mode="wait">
            <motion.div
              key={location}
              initial={{ opacity: 0, y: 20, filter: 'blur(10px)' }}
              animate={{ opacity: 1, y: 0, filter: 'blur(0px)' }}
              exit={{ opacity: 0, y: -20, filter: 'blur(10px)' }}
              transition={{ duration: 0.4, ease: "easeOut" }}
              className="max-w-7xl mx-auto h-full"
            >
              {children}
            </motion.div>
          </AnimatePresence>
        </div>
      </main>
    </div>
  );
}

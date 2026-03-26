import { Switch, Route, Router as WouterRouter } from "wouter";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import { AppStateContext, useAppStateInit } from "@/hooks/use-app-state";
import { Layout } from "@/components/Layout";
import Dashboard from "@/pages/Dashboard";
import BudgetPlanner from "@/pages/BudgetPlanner";
import SavingsGoals from "@/pages/SavingsGoals";
import AiAdvisor from "@/pages/AiAdvisor";
import Transactions from "@/pages/Transactions";
import Reports from "@/pages/Reports";
import NotFound from "@/pages/not-found";

const queryClient = new QueryClient();

function Router() {
  return (
    <Layout>
      <Switch>
        <Route path="/" component={Dashboard} />
        <Route path="/budget" component={BudgetPlanner} />
        <Route path="/goals" component={SavingsGoals} />
        <Route path="/ai-advisor" component={AiAdvisor} />
        <Route path="/transactions" component={Transactions} />
        <Route path="/reports" component={Reports} />
        <Route component={NotFound} />
      </Switch>
    </Layout>
  );
}

function App() {
  const appState = useAppStateInit();

  return (
    <AppStateContext.Provider value={appState}>
      <QueryClientProvider client={queryClient}>
        <TooltipProvider>
          <WouterRouter base={import.meta.env.BASE_URL.replace(/\/$/, "")}>
            <Router />
          </WouterRouter>
          <Toaster />
        </TooltipProvider>
      </QueryClientProvider>
    </AppStateContext.Provider>
  );
}

export default App;

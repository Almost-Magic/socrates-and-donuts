import { ReactNode } from 'react';
import Sidebar from './Sidebar';
import ThemeToggle from './ThemeToggle';

interface LayoutProps {
  children: ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  return (
    <div className="min-h-screen bg-midnight-900 text-gray-100">
      <div className="flex min-h-screen">
        {/* Desktop Sidebar */}
        <aside className="hidden lg:flex flex-col w-64 border-r border-midnight-700 bg-midnight-800/50">
          <Sidebar />
        </aside>

        {/* Main Content */}
        <main className="flex-1 flex flex-col">
          <header className="h-16 flex items-center justify-between px-6 border-b border-midnight-700">
            <h1 className="text-xl font-semibold text-gold">Socrates & Donuts</h1>
            <ThemeToggle />
          </header>
          <div className="flex-1 overflow-auto">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}

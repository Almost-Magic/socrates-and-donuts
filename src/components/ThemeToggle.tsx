import { useEffect, useState } from 'react';
import { Sun, Moon } from 'lucide-react';

export default function ThemeToggle() {
  const [isDark, setIsDark] = useState(true);

  useEffect(() => {
    const saved = localStorage.getItem('snd-theme');
    if (saved) {
      setIsDark(saved === 'dark');
    } else {
      setIsDark(true); // Default dark
    }
  }, []);

  useEffect(() => {
    document.documentElement.classList.toggle('dark', isDark);
    localStorage.setItem('snd-theme', isDark ? 'dark' : 'light');
  }, [isDark]);

  return (
    <button
      onClick={() => setIsDark(!isDark)}
      className="p-2 rounded-lg hover:bg-midnight-700 transition-colors"
      aria-label="Toggle theme"
    >
      {isDark ? <Sun size={20} className="text-gold" /> : <Moon size={20} />}
    </button>
  );
}

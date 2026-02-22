import { useState } from 'react';
import { Sun, Moon } from 'lucide-react';

export default function ThemeToggle() {
  const [isDark, setIsDark] = useState(true);

  const toggleTheme = () => {
    const newIsDark = !isDark;
    setIsDark(newIsDark);
    document.documentElement.setAttribute('data-theme', newIsDark ? 'dark' : 'light');
  };

  return (
    <button
      onClick={toggleTheme}
      className="p-2 rounded-lg hover:bg-midnight-700 transition-colors"
      aria-label="Toggle theme"
    >
      {isDark ? <Sun size={20} className="text-gold" /> : <Moon size={20} />}
    </button>
  );
}

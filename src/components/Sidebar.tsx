import { NavLink } from 'react-router-dom';
import { useState } from 'react';
import { Menu, X, HelpCircle, Settings } from 'lucide-react';

const navItems = [
  { path: '/', label: 'Home', icon: '🏠' },
  { path: '/mirror', label: 'The Mirror', icon: '🪞' },
  { path: '/vault', label: 'The Vault', icon: '🔐' },
  { path: '/letter', label: 'Letter', icon: '🔥' },
  { path: '/weather', label: 'Weather', icon: '🌤️' },
  { path: '/body', label: 'Body', icon: '🧭' },
  { path: '/decisions', label: 'Decisions', icon: '📔' },
  { path: '/rewriter', label: 'Rewriter', icon: '✍️' },
  { path: '/wisdom', label: 'Wisdom', icon: '📜' },
  { path: '/capture', label: 'Capture', icon: '⚡' },
];

export default function Sidebar() {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <div className={`flex flex-col ${collapsed ? 'w-16' : 'w-64'} transition-all duration-300`}>
      <div className="h-16 flex items-center justify-between px-4 border-b border-midnight-700">
        {!collapsed && (
          <span className="font-semibold text-gold">S&D</span>
        )}
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="p-2 hover:bg-midnight-700 rounded-lg transition-colors"
        >
          {collapsed ? <Menu size={20} /> : <X size={20} />}
        </button>
      </div>

      <nav className="flex-1 py-4 overflow-y-auto">
        <ul className="space-y-1 px-2">
          {navItems.map((item) => (
            <li key={item.path}>
              <NavLink
                to={item.path}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-2 rounded-lg transition-colors ${
                    isActive
                      ? 'bg-midnight-700 text-gold'
                      : 'hover:bg-midnight-700/50 text-gray-300'
                  }`
                }
              >
                <span>{item.icon}</span>
                {!collapsed && <span>{item.label}</span>}
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>

      <div className="p-4 border-t border-midnight-700 space-y-2">
        <button className="w-full flex items-center gap-3 px-3 py-2 hover:bg-midnight-700 rounded-lg transition-colors text-gray-300">
          <HelpCircle size={20} />
          {!collapsed && <span>Help</span>}
        </button>
        <button className="w-full flex items-center gap-3 px-3 py-2 hover:bg-midnight-700 rounded-lg transition-colors text-gray-300">
          <Settings size={20} />
          {!collapsed && <span>Settings</span>}
        </button>
      </div>
    </div>
  );
}

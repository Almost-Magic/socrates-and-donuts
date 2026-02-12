import { NavLink } from 'react-router-dom';
import {
  HomeIcon,
  UserGroupIcon,
  BuildingOfficeIcon,
  CurrencyDollarIcon,
  ChatBubbleLeftRightIcon,
  HandRaisedIcon,
  ClipboardDocumentCheckIcon,
  ShieldCheckIcon,
  ArrowsRightLeftIcon,
  SparklesIcon,
  ChartBarIcon,
  Cog6ToothIcon,
} from '@heroicons/react/24/outline';

const navItems = [
  { to: '/', label: 'Dashboard', icon: HomeIcon },
  { to: '/contacts', label: 'Contacts', icon: UserGroupIcon },
  { to: '/companies', label: 'Companies', icon: BuildingOfficeIcon },
  { to: '/deals', label: 'Deals', icon: CurrencyDollarIcon },
  { to: '/interactions', label: 'Interactions', icon: ChatBubbleLeftRightIcon },
  { to: '/commitments', label: 'Commitments', icon: HandRaisedIcon },
  { to: '/tasks', label: 'Tasks', icon: ClipboardDocumentCheckIcon },
  { to: '/privacy', label: 'Transparency', icon: ShieldCheckIcon },
  { to: '/import-export', label: 'Import/Export', icon: ArrowsRightLeftIcon },
  { to: '/intelligence', label: 'Intelligence', icon: SparklesIcon },
  { to: '/deal-analytics', label: 'Deal Analytics', icon: ChartBarIcon },
  { to: '/settings', label: 'Settings', icon: Cog6ToothIcon },
];

export default function Sidebar() {
  return (
    <aside className="w-56 bg-surface dark:bg-surface border-r border-border flex flex-col shrink-0 h-screen sticky top-0">
      <div className="p-4 border-b border-border">
        <div className="flex items-center gap-2">
          <span className="text-2xl">🌊</span>
          <div>
            <h1 className="font-heading text-lg font-semibold text-text-primary leading-tight">Ripple</h1>
            <p className="text-xs text-text-muted">Relationship Intelligence</p>
          </div>
        </div>
      </div>
      <nav className="flex-1 py-2 overflow-y-auto">
        {navItems.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) =>
              `flex items-center gap-3 px-4 py-2.5 mx-2 rounded-lg text-sm transition-colors ${
                isActive
                  ? 'bg-gold/10 text-gold font-medium'
                  : 'text-text-secondary hover:text-text-primary hover:bg-surface-light'
              }`
            }
          >
            <Icon className="w-5 h-5 shrink-0" />
            {label}
          </NavLink>
        ))}
      </nav>
      <div className="p-3 border-t border-border text-center">
        <p className="text-[10px] text-text-muted leading-tight">
          Made with ❤️ by Mani Padisetti<br />@ Almost Magic Tech Lab
        </p>
      </div>
    </aside>
  );
}

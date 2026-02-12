import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from './lib/theme';
import Layout from './components/Layout';
import ToastContainer from './components/Toast';
import Dashboard from './pages/Dashboard';
import Contacts from './pages/Contacts';
import ContactDetail from './pages/ContactDetail';
import Companies from './pages/Companies';
import Deals from './pages/Deals';
import Interactions from './pages/Interactions';
import Commitments from './pages/Commitments';
import Tasks from './pages/Tasks';
import Privacy from './pages/Privacy';
import ImportExport from './pages/ImportExport';
import Intelligence from './pages/Intelligence';
import DealAnalytics from './pages/DealAnalytics';
import Settings from './pages/Settings';

export default function App() {
  return (
    <ThemeProvider>
      <BrowserRouter>
        <Routes>
          <Route element={<Layout />}>
            <Route path="/" element={<Dashboard />} />
            <Route path="/contacts" element={<Contacts />} />
            <Route path="/contacts/:id" element={<ContactDetail />} />
            <Route path="/companies" element={<Companies />} />
            <Route path="/deals" element={<Deals />} />
            <Route path="/interactions" element={<Interactions />} />
            <Route path="/commitments" element={<Commitments />} />
            <Route path="/tasks" element={<Tasks />} />
            <Route path="/privacy" element={<Privacy />} />
            <Route path="/import-export" element={<ImportExport />} />
            <Route path="/intelligence" element={<Intelligence />} />
            <Route path="/deal-analytics" element={<DealAnalytics />} />
            <Route path="/settings" element={<Settings />} />
          </Route>
        </Routes>
      </BrowserRouter>
      <ToastContainer />
    </ThemeProvider>
  );
}

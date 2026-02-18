import { Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import LandingPage from './features/landing/LandingPage';
import Mirror from './features/mirror/Mirror';
import Vault from './features/vault/Vault';
import Letter from './features/letter/Letter';
import WeatherMap from './features/weather-map/WeatherMap';
import BodyCompass from './features/body-compass/BodyCompass';
import DecisionJournal from './features/decisions/DecisionJournal';
import Rewriter from './features/rewriter/Rewriter';
import WisdomFeed from './features/wisdom-feed/WisdomFeed';
import QuickCapture from './features/capture/QuickCapture';

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/mirror" element={<Mirror />} />
        <Route path="/vault" element={<Vault />} />
        <Route path="/letter" element={<Letter />} />
        <Route path="/weather" element={<WeatherMap />} />
        <Route path="/body" element={<BodyCompass />} />
        <Route path="/decisions" element={<DecisionJournal />} />
        <Route path="/rewriter" element={<Rewriter />} />
        <Route path="/wisdom" element={<WisdomFeed />} />
        <Route path="/capture" element={<QuickCapture />} />
      </Routes>
    </Layout>
  );
}

export default App;

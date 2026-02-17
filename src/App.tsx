import { useEffect } from 'react';
import Layout from './components/Layout';
import LandingPage from './features/landing/LandingPage';

function App() {
  // const [hasVisited, setHasVisited] = useState(false);

  useEffect(() => {
    const visited = localStorage.getItem('snd-has-visited');
    if (visited) {
      // setHasVisited(true);
    }
  }, []);

  // For now, always show landing page
  // Once features are built, this would route to app after first visit
  return (
    <Layout>
      <LandingPage />
    </Layout>
  );
}

export default App;

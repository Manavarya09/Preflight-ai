import { ThemeProvider } from 'styled-components';
import { useRef, useState, useEffect } from 'react';
import 'locomotive-scroll/dist/locomotive-scroll.css';
import { AnimatePresence } from 'framer-motion';
import { useLocation } from 'react-router-dom';
import SafeLocomotiveScrollProvider from './components/SafeLocomotiveScrollProvider';
import LocomotiveScrollErrorBoundary from './components/LocomotiveScrollErrorBoundary';

import GlobalStyles from './styles/GlobalStyles';
import { dark } from './styles/Themes';
import Home from './components/sections/Home';
import About from './components/sections/About';
import Second from './components/sections/Second';
import ScrollTriggerProxy from './components/ScrollTriggerProxy';
import Banner from './components/sections/Banner';
import Third from './components/sections/Third';
import Footer from './components/sections/Footer';
import Loader from './components/Loader';
import Faq from './components/sections/Faq';
import Our from './components/sections/Our';
import Suite from './components/sections/Suite';
import Dashboard from './components/sections/Dashboard';
import Alerts from './components/sections/Alerts';
import Analytics from './components/sections/Analytics';
import Insights from './components/sections/Insights';
import SystemPage from './components/sections/SystemPage';
import Settings from './components/sections/Settings';
import Profile from './components/sections/Profile';
import useSuppressScrollErrors from './hooks/useSuppressScrollErrors';

const App = () => {
  const containerRef = useRef(null);
  const location = useLocation();

  const [loaded, setLoaded] = useState(false);

  // Suppress LocomotiveScroll transform errors
  useSuppressScrollErrors();

  useEffect(() => {
    setTimeout(() => {
      setLoaded(true);
    }, 3000);
  }, []);

  const dashboardPages = ['/dashboard', '/alerts', '/analytics', '/insights', '/system', '/settings', '/profile'];
  const isDashboardPage = dashboardPages.includes(location.pathname);

  // Clean up LocomotiveScroll when switching to dashboard
  useEffect(() => {
    if (isDashboardPage && containerRef.current) {
      // Clear any locomotive scroll instances
      containerRef.current = null;
    }
  }, [isDashboardPage]);

  const renderDashboardPage = () => {
    switch (location.pathname) {
      case '/dashboard':
        return <Dashboard />;
      case '/alerts':
        return <Alerts />;
      case '/analytics':
        return <Analytics />;
      case '/insights':
        return <Insights />;
      case '/system':
        return <SystemPage />;
      case '/settings':
        return <Settings />;
      case '/profile':
        return <Profile />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <>
      <GlobalStyles />
      <ThemeProvider theme={dark}>
        {isDashboardPage ? (
          <AnimatePresence mode="wait">
            {loaded ? renderDashboardPage() : <Loader />}
          </AnimatePresence>
        ) : (
          <LocomotiveScrollErrorBoundary>
            <SafeLocomotiveScrollProvider
              key="landing-page"
              options={{
                smooth: true,
                smartphone: {
                  smooth: true,
                },
                tablet: {
                  smooth: true,
                },
                resetNativeScroll: true,
              }}
              watch={[location.pathname]}
              containerRef={containerRef}
            >
              <AnimatePresence>
                {loaded ? null : <Loader />}
              </AnimatePresence>
              <ScrollTriggerProxy />
            <AnimatePresence>
              <main
                className="App"
                data-scroll-container
                ref={containerRef}
              >
                <Home />
                <About />
                <Second />
                <Banner />
                <Third />
                <Faq/>
                <Our/>
                <Suite/>
                <Footer />
              </main>
            </AnimatePresence>
          </SafeLocomotiveScrollProvider>
          </LocomotiveScrollErrorBoundary>
        )}
      </ThemeProvider>
    </>
  );
};

export default App;

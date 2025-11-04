import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import styled from 'styled-components';
import '../dashboard.css';

const PageContainer = styled.div`
  width: 100%;
  min-height: 100vh;
  background: url('/src/assets/images/back.png') center/cover no-repeat;
  background-attachment: fixed;
  position: relative;
  color: #B6FF2B;
  font-family: 'Noto Sans', 'Inter', 'Manrope', sans-serif;
  padding-top: 4rem;

  &::before {
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.75);
    pointer-events: none;
    z-index: 0;
  }

  > * {
    position: relative;
    z-index: 1;
  }
`;

const HeaderNav = styled.nav`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
  background: rgba(15, 15, 15, 0.95);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(182, 255, 43, 0.15);
  padding: 0.8rem 2rem;
`;

const NavContent = styled.div`
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 3rem;

  .nav-logo {
    font-size: 1.3rem;
    font-weight: 700;
    color: #B6FF2B;
    letter-spacing: 0.5px;
    flex-shrink: 0;
  }

  .nav-tabs {
    display: flex;
    gap: 2.5rem;
    align-items: center;
    flex: 1;

    a, div {
      color: rgba(255, 255, 255, 0.7);
      text-decoration: none;
      font-size: 0.85rem;
      position: relative;
      transition: color 0.2s ease;
      cursor: pointer;
      font-weight: 500;
      letter-spacing: 0.3px;

      &.active {
        color: #B6FF2B;

        &::after {
          content: '';
          position: absolute;
          bottom: -10px;
          left: 0;
          right: 0;
          height: 2px;
          background: #B6FF2B;
          animation: slideIn 0.3s ease;
        }
      }

      &:hover {
        color: #B6FF2B;
      }
    }
  }

  .nav-actions {
    display: flex;
    gap: 0.8rem;
    flex-shrink: 0;

    button, a {
      background: transparent;
      color: rgba(182, 255, 43, 0.8);
      border: 1px solid rgba(182, 255, 43, 0.5);
      padding: 0.45rem 1rem;
      border-radius: 5px;
      cursor: pointer;
      font-size: 0.8rem;
      font-weight: 500;
      transition: all 0.2s ease;
      text-decoration: none;
      display: inline-block;

      &:hover {
        background: rgba(182, 255, 43, 0.15);
        color: #B6FF2B;
        border-color: #B6FF2B;
      }
    }
  }
`;

const MainContent = styled.div`
  max-width: 1000px;
  margin: 0 auto;
  padding: 2.5rem 2rem;
  display: grid;
  grid-template-columns: 1fr;
  gap: 2.5rem;
`;

const PageTitle = styled.h1`
  font-size: 2rem;
  font-weight: 700;
  color: #B6FF2B;
  margin-bottom: 0.5rem;
  letter-spacing: 0.5px;
`;

const PageSubtitle = styled.p`
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.95rem;
  margin-bottom: 2rem;
`;

const InsightCard = styled(motion.div)`
  background: rgba(182, 255, 43, 0.02);
  border: 1px solid rgba(182, 255, 43, 0.12);
  border-radius: 8px;
  padding: 1.8rem;

  .insight-title {
    font-size: 1.15rem;
    font-weight: 700;
    color: #B6FF2B;
    margin-bottom: 1rem;
  }

  .insight-content {
    color: rgba(255, 255, 255, 0.8);
    line-height: 1.8;
    font-size: 0.95rem;
    margin-bottom: 1.5rem;
  }

  .insight-metrics {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 1rem;
    padding: 1rem;
    background: rgba(182, 255, 43, 0.04);
    border-radius: 6px;

    .metric {
      .label {
        color: rgba(255, 255, 255, 0.5);
        font-size: 0.75rem;
        text-transform: uppercase;
        font-weight: 600;
        margin-bottom: 0.3rem;
      }

      .value {
        color: #B6FF2B;
        font-weight: 700;
        font-size: 1.2rem;
      }
    }
  }
`;

const Insights = () => {
  const insights = [
    {
      title: 'Weather Impact Analysis',
      content: 'Weather-related congestion increased average delay risk by 18% across major hubs this morning. Current meteorological patterns suggest continued elevated risk through the next 6 hours. System recommends optimizing flight schedules accordingly.'
    },
    {
      title: 'Gate Congestion Trends',
      content: 'Gate allocation efficiency has improved by 12% following recent procedural changes. Peak congestion periods are shifting to 14:00-16:00 UTC. Consider pre-positioning aircraft to secondary gates during peak hours.'
    },
    {
      title: 'ATC Flow Control Status',
      content: 'ATC flow control measures are currently in effect at 5 international airports. Expected duration: 3-4 hours. Primary affected routes show 25-35% delay increase. Alternative routing recommended for long-haul departures.'
    }
  ];

  return (
    <PageContainer>
      <HeaderNav>
        <NavContent>
          <Link to="/" style={{ textDecoration: 'none' }}>
            <div className="nav-logo">PreFlight AI</div>
          </Link>
          <div className="nav-tabs">
            <Link to="/dashboard">Dashboard</Link>
            <Link to="/alerts">Alerts</Link>
            <Link to="/analytics">Analytics</Link>
            <div className="active">Insights</div>
            <Link to="/system">System</Link>
          </div>
          <div className="nav-actions">
            <Link to="/settings"><button>Settings</button></Link>
            <Link to="/profile"><button>Profile</button></Link>
          </div>
        </NavContent>
      </HeaderNav>

      <MainContent>
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <PageTitle>AI Insights & Analysis</PageTitle>
          <PageSubtitle>Real-time insights from predictive models and data analysis</PageSubtitle>
        </motion.div>

        <div style={{ display: 'grid', gap: '1.5rem' }}>
          {insights.map((insight, idx) => (
            <InsightCard
              key={idx}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.15 }}
            >
              <div className="insight-title">{insight.title}</div>
              <div className="insight-content">{insight.content}</div>
              <div className="insight-metrics">
                <div className="metric">
                  <div className="label">Confidence</div>
                  <div className="value">94%</div>
                </div>
                <div className="metric">
                  <div className="label">Impact Level</div>
                  <div className="value">High</div>
                </div>
              </div>
            </InsightCard>
          ))}
        </div>
      </MainContent>
    </PageContainer>
  );
};

export default Insights;

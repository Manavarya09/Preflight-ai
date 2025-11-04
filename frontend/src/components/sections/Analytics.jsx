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
  max-width: 1400px;
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

const ChartsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 2rem;
`;

const ChartCard = styled(motion.div)`
  background: rgba(182, 255, 43, 0.02);
  border: 1px solid rgba(182, 255, 43, 0.12);
  border-radius: 8px;
  padding: 1.8rem;

  .chart-title {
    font-size: 1.1rem;
    font-weight: 700;
    color: #B6FF2B;
    margin-bottom: 1.5rem;
    letter-spacing: 0.3px;
  }

  .chart-content {
    height: 200px;
    background: rgba(0, 0, 0, 0.2);
    border-radius: 6px;
    display: flex;
    align-items: flex-end;
    justify-content: space-around;
    padding: 1rem;
    gap: 0.8rem;
  }

  .bar {
    flex: 1;
    background: #B6FF2B;
    border-radius: 4px 4px 0 0;
    transition: all 0.2s ease;

    &:hover {
      background: #c8ff47;
      filter: brightness(1.1);
    }
  }
`;

const StatsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
`;

const StatCard = styled(motion.div)`
  background: rgba(182, 255, 43, 0.04);
  border: 1px solid rgba(182, 255, 43, 0.15);
  padding: 1.5rem;
  border-radius: 8px;
  transition: all 0.25s ease;

  &:hover {
    background: rgba(182, 255, 43, 0.08);
    transform: translateY(-2px);
  }

  .stat-label {
    font-size: 0.75rem;
    color: rgba(255, 255, 255, 0.5);
    margin-bottom: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    font-weight: 600;
  }

  .stat-value {
    font-size: 1.85rem;
    font-weight: 700;
    color: #B6FF2B;
    margin-bottom: 0.6rem;
  }

  .stat-change {
    font-size: 0.7rem;
    color: rgba(182, 255, 43, 0.6);
    font-weight: 500;
  }
`;

const Analytics = () => {
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
            <div className="active">Analytics</div>
            <Link to="/insights">Insights</Link>
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
          <PageTitle>Analytics & Metrics</PageTitle>
          <PageSubtitle>Detailed performance metrics and predictive analytics</PageSubtitle>
        </motion.div>

        <StatsGrid>
          {[
            { label: 'Total Flights', value: '2,847', change: '+340 this month' },
            { label: 'Avg Accuracy', value: '94.2%', change: '+2.3% improvement' },
            { label: 'Critical Alerts', value: '47', change: '-15% from last week' },
            { label: 'System Uptime', value: '99.8%', change: 'All systems nominal' }
          ].map((stat, idx) => (
            <StatCard
              key={idx}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.1 }}
            >
              <div className="stat-label">{stat.label}</div>
              <div className="stat-value">{stat.value}</div>
              <div className="stat-change">{stat.change}</div>
            </StatCard>
          ))}
        </StatsGrid>

        <ChartsGrid>
          {[
            { title: 'Delay Distribution (Last 30 Days)', data: [15, 22, 18, 25, 20, 28, 19] },
            { title: 'Prediction Accuracy Trend', data: [89, 90, 91, 93, 92, 94, 94.2] },
            { title: 'Alerts by Severity', data: [35, 47, 18, 8] }
          ].map((chart, idx) => (
            <ChartCard
              key={idx}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: idx * 0.15 }}
            >
              <div className="chart-title">{chart.title}</div>
              <div className="chart-content">
                {chart.data.map((value, i) => (
                  <div
                    key={i}
                    className="bar"
                    style={{ height: `${(value / Math.max(...chart.data)) * 100}%` }}
                  />
                ))}
              </div>
            </ChartCard>
          ))}
        </ChartsGrid>
      </MainContent>
    </PageContainer>
  );
};

export default Analytics;

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

    button {
      background: transparent;
      color: rgba(182, 255, 43, 0.8);
      border: 1px solid rgba(182, 255, 43, 0.5);
      padding: 0.45rem 1rem;
      border-radius: 5px;
      cursor: pointer;
      font-size: 0.8rem;
      font-weight: 500;
      transition: all 0.2s ease;

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

const AlertsGrid = styled.div`
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.2rem;
`;

const AlertCard = styled(motion.div)`
  background: rgba(182, 255, 43, 0.05);
  border: 1px solid rgba(182, 255, 43, 0.1);
  border-radius: 7px;
  padding: 1.5rem;
  transition: all 0.25s ease;

  &:hover {
    background: rgba(182, 255, 43, 0.08);
    border-color: rgba(182, 255, 43, 0.2);
    transform: translateX(4px);
  }

  .alert-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 1rem;

    .alert-info {
      flex: 1;
    }

    .flight-id {
      color: #B6FF2B;
      font-weight: 700;
      font-size: 1.1rem;
      margin-bottom: 0.3rem;
    }

    .severity {
      display: inline-block;
      padding: 0.3rem 0.8rem;
      border-radius: 20px;
      font-size: 0.75rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.3px;

      &.critical {
        background: rgba(255, 100, 100, 0.2);
        color: #ff7a7a;
      }

      &.warning {
        background: rgba(255, 200, 0, 0.2);
        color: #ffc800;
      }

      &.info {
        background: rgba(100, 200, 255, 0.2);
        color: #64c8ff;
      }
    }

    .timestamp {
      color: rgba(255, 255, 255, 0.35);
      font-size: 0.75rem;
    }
  }

  .alert-content {
    color: rgba(255, 255, 255, 0.8);
    font-size: 0.9rem;
    line-height: 1.6;
    margin-bottom: 1rem;
  }

  .alert-details {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 1rem;
    margin-bottom: 1rem;
    padding: 1rem;
    background: rgba(182, 255, 43, 0.04);
    border-radius: 6px;

    .detail {
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
      }
    }
  }

  .alert-actions {
    display: flex;
    gap: 0.8rem;

    button {
      flex: 1;
      padding: 0.6rem 1rem;
      border: 1px solid rgba(182, 255, 43, 0.25);
      background: rgba(182, 255, 43, 0.08);
      color: #B6FF2B;
      border-radius: 5px;
      cursor: pointer;
      font-size: 0.8rem;
      font-weight: 600;
      transition: all 0.2s ease;

      &:hover {
        background: #B6FF2B;
        color: #000;
        border-color: #B6FF2B;
      }

      &.escalate {
        border-color: rgba(255, 100, 100, 0.25);
        color: #ff8888;

        &:hover {
          background: #ff8888;
          color: #fff;
          border-color: #ff8888;
        }
      }
    }
  }
`;

const Alerts = () => {
  const mockAlerts = [
    {
      id: 'ALERT001',
      flight: 'SQ006',
      severity: 'critical',
      cause: 'ATC Flow Control - Heavy traffic in airspace',
      probability: 92,
      delay: 45,
      timestamp: '2 minutes ago',
      route: 'SIN → LHR'
    },
    {
      id: 'ALERT002',
      flight: 'EK230',
      severity: 'warning',
      cause: 'Gate Congestion - Multiple departures delayed',
      probability: 78,
      delay: 23,
      timestamp: '5 minutes ago',
      route: 'LAX → DXB'
    },
    {
      id: 'ALERT003',
      flight: 'BA115',
      severity: 'info',
      cause: 'Weather System - Storm approaching airport',
      probability: 45,
      delay: 12,
      timestamp: '8 minutes ago',
      route: 'LHR → JFK'
    },
    {
      id: 'ALERT004',
      flight: 'LH720',
      severity: 'warning',
      cause: 'Maintenance delay - Aircraft pre-flight checks',
      probability: 55,
      delay: 18,
      timestamp: '12 minutes ago',
      route: 'FRA → NRT'
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
            <div className="active">Alerts</div>
            <Link to="/analytics">Analytics</Link>
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
          <PageTitle>Real-Time Alerts</PageTitle>
          <PageSubtitle>Active alerts and notifications from your flight operations</PageSubtitle>
        </motion.div>

        <AlertsGrid>
          {mockAlerts.map((alert, idx) => (
            <AlertCard
              key={alert.id}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: idx * 0.1 }}
            >
              <div className="alert-header">
                <div className="alert-info">
                  <div className="flight-id">{alert.flight}</div>
                  <span className={`severity ${alert.severity}`}>{alert.severity}</span>
                </div>
                <div className="timestamp">{alert.timestamp}</div>
              </div>

              <div className="alert-content">{alert.cause}</div>

              <div className="alert-details">
                <div className="detail">
                  <div className="label">Route</div>
                  <div className="value">{alert.route}</div>
                </div>
                <div className="detail">
                  <div className="label">Probability</div>
                  <div className="value">{alert.probability}%</div>
                </div>
                <div className="detail">
                  <div className="label">Predicted Delay</div>
                  <div className="value">{alert.delay} min</div>
                </div>
                <div className="detail">
                  <div className="label">Alert ID</div>
                  <div className="value">{alert.id}</div>
                </div>
              </div>

              <div className="alert-actions">
                <button>Acknowledge</button>
                <button className="escalate">Escalate</button>
              </div>
            </AlertCard>
          ))}
        </AlertsGrid>
      </MainContent>
    </PageContainer>
  );
};

export default Alerts;

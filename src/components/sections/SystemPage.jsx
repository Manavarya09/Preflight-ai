import React, { useState } from 'react';
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

const SystemCard = styled(motion.div)`
  background: rgba(182, 255, 43, 0.02);
  border: 1px solid rgba(182, 255, 43, 0.12);
  border-radius: 8px;
  padding: 1.8rem;

  .card-title {
    font-size: 1.15rem;
    font-weight: 700;
    color: #B6FF2B;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    gap: 0.8rem;

    .status-badge {
      display: inline-block;
      width: 10px;
      height: 10px;
      border-radius: 50%;
      background: #00ff00;
      
      &.warning {
        background: #ffc800;
      }

      &.critical {
        background: #ff7a7a;
      }
    }
  }

  .system-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.9rem 0;
    border-bottom: 1px solid rgba(182, 255, 43, 0.06);

    .item-name {
      color: rgba(255, 255, 255, 0.75);
      font-weight: 600;
    }

    .item-status {
      display: flex;
      align-items: center;
      gap: 0.5rem;

      .status-text {
        color: #B6FF2B;
        font-weight: 700;
      }

      .status-indicator {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #00ff00;
      }
    }

    &:last-child {
      border-bottom: none;
    }
  }
`;

const SystemPage = () => {

  const systems = [
    {
      title: 'Backend Services',
      status: 'online',
      items: [
        { name: 'FastAPI Server', status: 'operational' },
        { name: 'Langflow Service', status: 'operational' },
        { name: 'n8n Workflow Engine', status: 'operational' },
        { name: 'Ollama LLM Service', status: 'operational' }
      ]
    },
    {
      title: 'Database Services',
      status: 'online',
      items: [
        { name: 'TimescaleDB (Primary)', status: 'operational' },
        { name: 'Redis Cache', status: 'operational' },
        { name: 'Backup Storage', status: 'operational' }
      ]
    },
    {
      title: 'Model Services',
      status: 'online',
      items: [
        { name: 'LSTM Predictor', status: 'operational' },
        { name: 'XGBoost Ensemble', status: 'operational' },
        { name: 'Prophet Forecaster', status: 'operational' }
      ]
    },
    {
      title: 'External Integrations',
      status: 'online',
      items: [
        { name: 'Weather API', status: 'operational' },
        { name: 'ATC Data Feed', status: 'operational' },
        { name: 'Fleet Management System', status: 'operational' }
      ]
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
            <Link to="/insights">Insights</Link>
            <div className="active">System</div>
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
          <PageTitle>System Status</PageTitle>
          <PageSubtitle>Monitor all backend services and integrations</PageSubtitle>
        </motion.div>

        <div style={{ display: 'grid', gap: '1.5rem' }}>
          {systems.map((system, idx) => (
            <SystemCard
              key={idx}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.1 }}
            >
              <div className="card-title">
                <div className="status-badge"></div>
                {system.title}
              </div>
              {system.items.map((item, i) => (
                <div key={i} className="system-item">
                  <div className="item-name">{item.name}</div>
                  <div className="item-status">
                    <span className="status-text">{item.status}</span>
                    <div className="status-indicator"></div>
                  </div>
                </div>
              ))}
            </SystemCard>
          ))}
        </div>
      </MainContent>
    </PageContainer>
  );
};

export default SystemPage;

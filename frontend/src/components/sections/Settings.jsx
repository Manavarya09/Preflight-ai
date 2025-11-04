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
  max-width: 900px;
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

const SettingSection = styled(motion.div)`
  background: rgba(182, 255, 43, 0.02);
  border: 1px solid rgba(182, 255, 43, 0.12);
  border-radius: 8px;
  padding: 1.8rem;

  .section-title {
    font-size: 1.15rem;
    font-weight: 700;
    color: #B6FF2B;
    margin-bottom: 1.5rem;
  }

  .setting-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 0;
    border-bottom: 1px solid rgba(182, 255, 43, 0.06);

    &:last-child {
      border-bottom: none;
    }

    .item-label {
      flex: 1;

      .label-title {
        color: rgba(255, 255, 255, 0.85);
        font-weight: 600;
        margin-bottom: 0.3rem;
      }

      .label-description {
        color: rgba(255, 255, 255, 0.45);
        font-size: 0.85rem;
      }
    }

    .item-control {
      select, input {
        background: rgba(0, 0, 0, 0.25);
        border: 1px solid rgba(182, 255, 43, 0.15);
        color: #B6FF2B;
        padding: 0.5rem 0.8rem;
        border-radius: 5px;
        font-size: 0.85rem;
        transition: all 0.2s ease;

        &:focus {
          outline: none;
          border-color: rgba(182, 255, 43, 0.5);
          background: rgba(0, 0, 0, 0.35);
        }
      }

      input[type="checkbox"] {
        width: 18px;
        height: 18px;
        cursor: pointer;
        accent-color: #B6FF2B;
      }

      input[type="range"] {
        width: 120px;
      }
    }
  }
`;

const SaveButton = styled.button`
  width: 100%;
  padding: 0.8rem;
  background: #B6FF2B;
  color: #000;
  border: none;
  border-radius: 6px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
  margin-top: 1.5rem;
  font-size: 0.95rem;

  &:hover {
    background: #a8f01e;
    transform: translateY(-1px);
    box-shadow: 0 8px 20px rgba(182, 255, 43, 0.25);
  }

  &:active {
    transform: translateY(0);
  }
`;

const Settings = () => {
  const [settings, setSettings] = useState({
    notifications: true,
    darkMode: true,
    updateFrequency: '10',
    alertThreshold: '60'
  });

  const handleChange = (key, value) => {
    setSettings(prev => ({ ...prev, [key]: value }));
  };

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
            <Link to="/system">System</Link>
          </div>
          <div className="nav-actions">
            <div className="active" style={{padding: '0.45rem 1rem', borderRadius: '5px', border: '1px solid rgba(182, 255, 43, 0.5)'}}>Settings</div>
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
          <PageTitle>Settings</PageTitle>
          <PageSubtitle>Configure your PreFlight AI experience</PageSubtitle>
        </motion.div>

        <SettingSection
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <div className="section-title">Notifications</div>
          
          <div className="setting-item">
            <div className="item-label">
              <div className="label-title">Enable Notifications</div>
              <div className="label-description">Receive alerts and updates</div>
            </div>
            <div className="item-control">
              <input
                type="checkbox"
                checked={settings.notifications}
                onChange={(e) => handleChange('notifications', e.target.checked)}
              />
            </div>
          </div>

          <div className="setting-item">
            <div className="item-label">
              <div className="label-title">Alert Threshold</div>
              <div className="label-description">Delay probability threshold</div>
            </div>
            <div className="item-control">
              <select
                value={settings.alertThreshold}
                onChange={(e) => handleChange('alertThreshold', e.target.value)}
              >
                <option value="40">40%</option>
                <option value="50">50%</option>
                <option value="60">60%</option>
                <option value="70">70%</option>
                <option value="80">80%</option>
              </select>
            </div>
          </div>
        </SettingSection>

        <SettingSection
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <div className="section-title">Display</div>
          
          <div className="setting-item">
            <div className="item-label">
              <div className="label-title">Dark Mode</div>
              <div className="label-description">Use dark theme</div>
            </div>
            <div className="item-control">
              <input
                type="checkbox"
                checked={settings.darkMode}
                onChange={(e) => handleChange('darkMode', e.target.checked)}
              />
            </div>
          </div>
        </SettingSection>

        <SettingSection
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <div className="section-title">Data Refresh</div>
          
          <div className="setting-item">
            <div className="item-label">
              <div className="label-title">Update Frequency</div>
              <div className="label-description">How often to refresh data</div>
            </div>
            <div className="item-control">
              <select
                value={settings.updateFrequency}
                onChange={(e) => handleChange('updateFrequency', e.target.value)}
              >
                <option value="5">Every 5 seconds</option>
                <option value="10">Every 10 seconds</option>
                <option value="30">Every 30 seconds</option>
                <option value="60">Every 60 seconds</option>
              </select>
            </div>
          </div>
        </SettingSection>

        <SaveButton>Save Settings</SaveButton>
      </MainContent>
    </PageContainer>
  );
};

export default Settings;

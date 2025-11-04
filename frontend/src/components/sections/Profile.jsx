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
  max-width: 800px;
  margin: 0 auto;
  padding: 2.5rem 2rem;
  display: grid;
  grid-template-columns: 1fr;
  gap: 2.5rem;
`;

const ProfileCard = styled(motion.div)`
  background: rgba(182, 255, 43, 0.02);
  border: 1px solid rgba(182, 255, 43, 0.12);
  border-radius: 8px;
  padding: 2rem;
  text-align: center;

  .profile-avatar {
    width: 100px;
    height: 100px;
    background: linear-gradient(135deg, rgba(182, 255, 43, 0.2), rgba(182, 255, 43, 0.1));
    border: 2px solid rgba(182, 255, 43, 0.3);
    border-radius: 50%;
    margin: 0 auto 1.5rem;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 3rem;
  }

  .profile-name {
    font-size: 1.8rem;
    font-weight: 700;
    color: #B6FF2B;
    margin-bottom: 0.5rem;
  }

  .profile-role {
    color: rgba(255, 255, 255, 0.6);
    font-size: 0.95rem;
    margin-bottom: 1.5rem;
  }
`;

const InfoGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.5rem;

  @media (max-width: 600px) {
    grid-template-columns: 1fr;
  }
`;

const InfoCard = styled(motion.div)`
  background: rgba(182, 255, 43, 0.02);
  border: 1px solid rgba(182, 255, 43, 0.12);
  border-radius: 8px;
  padding: 1.5rem;

  .info-label {
    color: rgba(255, 255, 255, 0.5);
    font-size: 0.75rem;
    text-transform: uppercase;
    font-weight: 600;
    margin-bottom: 0.6rem;
    letter-spacing: 0.3px;
  }

  .info-value {
    color: #B6FF2B;
    font-size: 1.1rem;
    font-weight: 700;
  }
`;

const ActionButtons = styled.div`
  display: flex;
  gap: 1rem;

  button {
    flex: 1;
    padding: 0.8rem;
    border: 1px solid rgba(182, 255, 43, 0.25);
    background: rgba(182, 255, 43, 0.08);
    color: #B6FF2B;
    border-radius: 6px;
    font-weight: 700;
    cursor: pointer;
    transition: all 0.2s ease;
    font-size: 0.9rem;

    &:hover {
      background: #B6FF2B;
      color: #000;
      border-color: #B6FF2B;
    }

    &.danger {
      border-color: rgba(255, 100, 100, 0.25);
      color: #ff8888;

      &:hover {
        background: #ff8888;
        color: #fff;
        border-color: #ff8888;
      }
    }
  }
`;

const Profile = () => {
  const profileInfo = {
    name: 'Flight Operations Team',
    role: 'System Administrator',
    email: 'ops@preflightai.com',
    organization: 'International Aviation',
    memberSince: '2024-01-15',
    lastLogin: '5 minutes ago'
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
            <Link to="/settings"><button>Settings</button></Link>
            <div className="active" style={{padding: '0.45rem 1rem', borderRadius: '5px', border: '1px solid rgba(182, 255, 43, 0.5)'}}>Profile</div>
          </div>
        </NavContent>
      </HeaderNav>

      <MainContent>
        <ProfileCard
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <div className="profile-avatar">👤</div>
          <div className="profile-name">{profileInfo.name}</div>
          <div className="profile-role">{profileInfo.role}</div>
        </ProfileCard>

        <InfoGrid>
          <InfoCard
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            <div className="info-label">Email</div>
            <div className="info-value">{profileInfo.email}</div>
          </InfoCard>

          <InfoCard
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.15 }}
          >
            <div className="info-label">Organization</div>
            <div className="info-value">{profileInfo.organization}</div>
          </InfoCard>

          <InfoCard
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <div className="info-label">Member Since</div>
            <div className="info-value">{profileInfo.memberSince}</div>
          </InfoCard>

          <InfoCard
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.25 }}
          >
            <div className="info-label">Last Login</div>
            <div className="info-value">{profileInfo.lastLogin}</div>
          </InfoCard>
        </InfoGrid>

        <ActionButtons>
          <button>Edit Profile</button>
          <button>Change Password</button>
          <button className="danger">Logout</button>
        </ActionButtons>
      </MainContent>
    </PageContainer>
  );
};

export default Profile;

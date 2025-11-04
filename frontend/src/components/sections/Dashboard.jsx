import React, { useState, useEffect, useMemo } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import styled from 'styled-components';
import '../dashboard.css';
import { fetchFlights, getInsights, scoreFlight } from '../../utils/api';

const DashboardContainer = styled.div`
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

    a,
    div {
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

  @media (max-width: 1024px) {
    gap: 2rem;

    .nav-tabs {
      gap: 1.5rem;
    }
  }

  @media (max-width: 768px) {
    flex-wrap: wrap;
    gap: 1rem;

    .nav-tabs {
      gap: 1rem;
      order: 3;
      width: 100%;
      justify-content: center;
      font-size: 0.75rem;
    }

    .nav-logo {
      order: 1;
    }

    .nav-actions {
      order: 2;
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

  @media (max-width: 1024px) {
    padding: 2rem 1.5rem;
    gap: 2rem;
  }

  @media (max-width: 768px) {
    padding: 1.5rem 1rem;
    gap: 1.5rem;
  }
`;

const KPIGrid = styled(motion.div)`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1.5rem;

  @media (max-width: 1024px) {
    grid-template-columns: repeat(2, 1fr);
  }

  @media (max-width: 640px) {
    grid-template-columns: 1fr;
  }
`;

const KPICard = styled(motion.div)`
  background: rgba(182, 255, 43, 0.04);
  border: 1px solid rgba(182, 255, 43, 0.15);
  padding: 1.5rem;
  border-radius: 8px;
  transition: all 0.25s ease;

  &:hover {
    background: rgba(182, 255, 43, 0.08);
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(182, 255, 43, 0.08);
    border-color: rgba(182, 255, 43, 0.3);
  }

  .kpi-label {
    font-size: 0.75rem;
    color: rgba(255, 255, 255, 0.5);
    margin-bottom: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    font-weight: 600;
  }

  .kpi-value {
    font-size: 1.85rem;
    font-weight: 700;
    color: #B6FF2B;
    line-height: 1.1;
  }

  .kpi-change {
    font-size: 0.7rem;
    color: rgba(182, 255, 43, 0.6);
    margin-top: 0.8rem;
    font-weight: 500;
  }
`;

const FlightsSection = styled.div`
  display: grid;
  grid-template-columns: 1.2fr 1fr;
  gap: 2rem;

  @media (max-width: 1200px) {
    grid-template-columns: 1fr 1fr;
  }

  @media (max-width: 1024px) {
    grid-template-columns: 1fr;
  }
`;

const FlightsTable = styled.div`
  background: rgba(182, 255, 43, 0.02);
  border: 1px solid rgba(182, 255, 43, 0.12);
  border-radius: 8px;
  overflow: hidden;

  .table-header {
    display: grid;
    grid-template-columns: 1fr 1.5fr 1fr 1.2fr 1fr;
    gap: 1rem;
    background: rgba(182, 255, 43, 0.07);
    padding: 0.95rem 1.2rem;
    border-bottom: 1px solid rgba(182, 255, 43, 0.15);
    font-weight: 600;
    font-size: 0.85rem;
    color: #B6FF2B;
    position: sticky;
    top: 0;
    letter-spacing: 0.3px;

    @media (max-width: 768px) {
      grid-template-columns: 1fr 1fr 1fr;
      font-size: 0.75rem;
      padding: 0.8rem 1rem;
    }
  }

  .table-body {
    max-height: 450px;
    overflow-y: auto;
  }

  .table-row {
    display: grid;
    grid-template-columns: 1fr 1.5fr 1fr 1.2fr 1fr;
    gap: 1rem;
    padding: 0.9rem 1.2rem;
    border-bottom: 1px solid rgba(182, 255, 43, 0.06);
    align-items: center;
    cursor: pointer;
    transition: all 0.25s ease;

    @media (max-width: 768px) {
      grid-template-columns: 1fr 1fr 1fr;
      padding: 0.8rem 1rem;

      .delay-reason,
      .predicted-delay {
        display: none;
      }
    }

    &:hover {
      background: rgba(182, 255, 43, 0.06);
    }

    &.selected {
      background: rgba(182, 255, 43, 0.1);
      border-left: 3px solid #B6FF2B;
    }

    .flight-id {
      font-weight: 700;
      color: #B6FF2B;
      font-size: 0.95rem;
    }

    .route {
      color: rgba(255, 255, 255, 0.75);
      font-size: 0.85rem;
      font-weight: 500;
    }

    .delay-probability {
      font-weight: 700;
      padding: 0.35rem 0.7rem;
      border-radius: 5px;
      text-align: center;
      font-size: 0.85rem;

      &.green {
        background: rgba(0, 255, 0, 0.15);
        color: #7bff00;
      }

      &.yellow {
        background: rgba(255, 200, 0, 0.2);
        color: #ffc800;
      }

      &.red {
        background: rgba(255, 100, 100, 0.18);
        color: #ff7a7a;
      }
    }

    .predicted-delay {
      color: rgba(255, 255, 255, 0.75);
      font-weight: 500;
      font-size: 0.9rem;
    }

    .status {
      padding: 0.35rem 0.7rem;
      border-radius: 5px;
      font-size: 0.8rem;
      text-align: center;
      background: rgba(182, 255, 43, 0.12);
      color: #B6FF2B;
      font-weight: 600;
    }
  }
`;

const SearchBar = styled.div`
  padding: 1rem 1.2rem 0.8rem;
  border-bottom: 1px solid rgba(182, 255, 43, 0.08);

  input {
    width: 100%;
    background: rgba(0, 0, 0, 0.25);
    border: 1px solid rgba(182, 255, 43, 0.15);
    color: #fff;
    padding: 0.7rem 1rem;
    border-radius: 6px;
    font-size: 0.9rem;
    transition: all 0.2s ease;

    &::placeholder {
      color: rgba(255, 255, 255, 0.35);
    }

    &:focus {
      outline: none;
      border-color: rgba(182, 255, 43, 0.5);
      background: rgba(0, 0, 0, 0.35);
      box-shadow: 0 0 12px rgba(182, 255, 43, 0.15);
    }
  }
`;

const FlightDetailPanel = styled(motion.div)`
  background: rgba(182, 255, 43, 0.02);
  border: 1px solid rgba(182, 255, 43, 0.12);
  border-radius: 8px;
  padding: 1.8rem;
  height: fit-content;
  max-height: 600px;
  overflow-y: auto;

  .detail-title {
    font-size: 1.15rem;
    font-weight: 700;
    color: #B6FF2B;
    margin-bottom: 1.5rem;
    letter-spacing: 0.3px;
  }

  .detail-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.85rem 0;
    border-bottom: 1px solid rgba(182, 255, 43, 0.07);

    label {
      color: rgba(255, 255, 255, 0.55);
      font-size: 0.85rem;
      font-weight: 600;
      letter-spacing: 0.3px;
    }

    span {
      color: #B6FF2B;
      font-weight: 700;
      font-size: 0.95rem;
    }

    &:last-of-type {
      border-bottom: none;
    }
  }

  .explanation {
    background: rgba(182, 255, 43, 0.07);
    border-left: 3px solid #B6FF2B;
    padding: 1rem 1.1rem;
    border-radius: 6px;
    margin: 1.5rem 0;
    color: rgba(255, 255, 255, 0.8);
    font-size: 0.85rem;
    line-height: 1.7;

    .exp-title {
      color: #B6FF2B;
      font-weight: 700;
      margin-bottom: 0.6rem;
      font-size: 0.9rem;
    }
  }

  .contributing-factors {
    margin: 1.5rem 0;

    .factors-title {
      color: #B6FF2B;
      font-weight: 700;
      margin-bottom: 1.1rem;
      font-size: 0.9rem;
      letter-spacing: 0.3px;
    }

    .factor-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 0.9rem;
      gap: 0.8rem;

      .factor-name {
        color: rgba(255, 255, 255, 0.65);
        font-size: 0.85rem;
        font-weight: 500;
        min-width: 110px;
      }

      .factor-bar {
        flex: 1;
        height: 5px;
        background: rgba(182, 255, 43, 0.12);
        border-radius: 3px;
        position: relative;
        overflow: hidden;

        .factor-fill {
          height: 100%;
          background: #B6FF2B;
          transition: width 0.5s ease;
        }
      }

      .factor-value {
        color: #B6FF2B;
        font-weight: 700;
        min-width: 35px;
        text-align: right;
        font-size: 0.85rem;
      }
    }
  }

  .notify-button {
    width: 100%;
    padding: 0.75rem;
    background: #B6FF2B;
    color: #000;
    border: none;
    border-radius: 6px;
    font-weight: 700;
    cursor: pointer;
    transition: all 0.2s ease;
    margin-top: 1.5rem;
    font-size: 0.9rem;

    &:hover {
      background: #a8f01e;
      transform: translateY(-1px);
      box-shadow: 0 8px 20px rgba(182, 255, 43, 0.25);
    }

    &:active {
      transform: translateY(0);
    }
  }
`;

const AlertsSection = styled.div`
  background: rgba(182, 255, 43, 0.02);
  border: 1px solid rgba(182, 255, 43, 0.12);
  border-radius: 8px;
  padding: 1.8rem;

  .alerts-title {
    font-size: 1.15rem;
    font-weight: 700;
    color: #B6FF2B;
    margin-bottom: 1.5rem;
    letter-spacing: 0.3px;
  }

  .alerts-list {
    max-height: 320px;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 0.8rem;
  }

  .alert-card {
    background: rgba(182, 255, 43, 0.05);
    border: 1px solid rgba(182, 255, 43, 0.1);
    border-radius: 7px;
    padding: 1rem;
    transition: all 0.25s ease;

    &:hover {
      background: rgba(182, 255, 43, 0.08);
      border-color: rgba(182, 255, 43, 0.2);
    }

    .alert-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 0.6rem;

      .flight-id {
        color: #B6FF2B;
        font-weight: 700;
        font-size: 0.95rem;
      }

      .timestamp {
        color: rgba(255, 255, 255, 0.35);
        font-size: 0.7rem;
        font-weight: 500;
      }
    }

    .alert-content {
      color: rgba(255, 255, 255, 0.7);
      font-size: 0.85rem;
      margin-bottom: 0.8rem;
      line-height: 1.6;
    }

    .alert-actions {
      display: flex;
      gap: 0.6rem;

      button {
        flex: 1;
        padding: 0.45rem 0.6rem;
        border: 1px solid rgba(182, 255, 43, 0.25);
        background: rgba(182, 255, 43, 0.08);
        color: #B6FF2B;
        border-radius: 5px;
        cursor: pointer;
        font-size: 0.75rem;
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
  }
`;

const InsightsSection = styled.div`
  background: rgba(182, 255, 43, 0.02);
  border: 1px solid rgba(182, 255, 43, 0.12);
  border-radius: 8px;
  padding: 1.8rem;

  .insights-title {
    font-size: 1.15rem;
    font-weight: 700;
    color: #B6FF2B;
    margin-bottom: 1.3rem;
    letter-spacing: 0.3px;
  }

  .insights-text {
    color: rgba(255, 255, 255, 0.8);
    line-height: 1.8;
    margin-bottom: 2rem;
    padding: 1.2rem;
    background: rgba(182, 255, 43, 0.06);
    border-left: 3px solid #B6FF2B;
    border-radius: 6px;
    font-size: 0.9rem;
  }

  .charts-container {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.5rem;

    @media (max-width: 1024px) {
      gap: 1.2rem;
    }

    @media (max-width: 768px) {
      grid-template-columns: 1fr;
      gap: 1rem;
    }
  }
`;

const ChartContainer = styled.div`
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(182, 255, 43, 0.12);
  padding: 1.2rem;
  border-radius: 7px;

  .chart-title {
    color: #B6FF2B;
    font-weight: 700;
    margin-bottom: 1.1rem;
    font-size: 0.9rem;
    letter-spacing: 0.3px;
  }
`;

const AdminPanel = styled.div`
  background: rgba(182, 255, 43, 0.02);
  border: 1px solid rgba(182, 255, 43, 0.12);
  border-radius: 8px;
  padding: 1.8rem;

  .admin-title {
    font-size: 1.15rem;
    font-weight: 700;
    color: #B6FF2B;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    letter-spacing: 0.3px;

    .toggle-btn {
      background: rgba(182, 255, 43, 0.12);
      border: 1px solid rgba(182, 255, 43, 0.3);
      color: #B6FF2B;
      padding: 0.4rem 0.9rem;
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
    }
  }

  .admin-content {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
    gap: 1rem;
  }

  .admin-item {
    background: rgba(182, 255, 43, 0.05);
    border: 1px solid rgba(182, 255, 43, 0.1);
    padding: 1rem;
    border-radius: 6px;
    transition: all 0.2s ease;

    &:hover {
      border-color: rgba(182, 255, 43, 0.2);
      background: rgba(182, 255, 43, 0.07);
    }

    .item-label {
      color: rgba(255, 255, 255, 0.5);
      font-size: 0.75rem;
      margin-bottom: 0.6rem;
      text-transform: uppercase;
      font-weight: 600;
      letter-spacing: 0.3px;
    }

    .item-value {
      color: #B6FF2B;
      font-weight: 700;
      margin-bottom: 0.8rem;
      font-size: 0.9rem;
    }

    select,
    input {
      width: 100%;
      background: rgba(0, 0, 0, 0.25);
      border: 1px solid rgba(182, 255, 43, 0.15);
      color: #B6FF2B;
      padding: 0.5rem 0.7rem;
      border-radius: 5px;
      font-size: 0.8rem;
      transition: all 0.2s ease;

      &:focus {
        outline: none;
        border-color: rgba(182, 255, 43, 0.5);
        background: rgba(0, 0, 0, 0.35);
      }
    }
  }
`;

const FooterSection = styled.footer`
  background: rgba(0, 0, 0, 0.4);
  border-top: 1px solid rgba(182, 255, 43, 0.12);
  padding: 2.5rem 2rem;
  text-align: center;
  margin-top: 3rem;
  color: rgba(255, 255, 255, 0.55);
  font-size: 0.85rem;

  .footer-text {
    margin-bottom: 1.2rem;
    line-height: 1.5;
    letter-spacing: 0.2px;
  }

  .footer-links {
    display: flex;
    justify-content: center;
    gap: 2.5rem;

    a {
      color: #B6FF2B;
      text-decoration: none;
      transition: all 0.2s ease;
      font-weight: 600;

      &:hover {
        color: #c8ff47;
      }
    }
  }

  @media (max-width: 768px) {
    padding: 2rem 1.5rem;

    .footer-links {
      gap: 1.5rem;
      font-size: 0.8rem;
    }
  }
`;

const DEFAULT_FACTORS = { crosswind: 0.2, gateOccupancy: 0.17, routeDelay: 0.14 };

const clampFactor = (value = 0) => {
  const numeric = Number.isFinite(value) ? Math.abs(value) : 0;
  return Math.max(0, Math.min(1, numeric));
};

const shapToFactors = (shap) => {
  if (!shap) return null;
  return {
    crosswind: clampFactor(shap.crosswind),
    gateOccupancy: clampFactor(shap.atc ?? shap.gate_congestion),
    routeDelay: clampFactor(shap.route_delay ?? shap.visibility),
  };
};

const buildDefaultPayload = (flightId) => {
  const now = new Date();
  const arrival = new Date(now.getTime() + 2 * 60 * 60 * 1000);
  return {
    flight_id: flightId,
    scheduled_departure: now.toISOString(),
    scheduled_arrival: arrival.toISOString(),
    weather: { wind_kts: 12, visibility_km: 8 },
    gate: 'A12',
    atc: 'flow control advisory',
  };
};

const mockFlights = [
  {
    id: 'EK230',
    origin: 'LAX',
    destination: 'DXB',
    delayProb: 0.78,
    predictedDelay: 23,
    status: 'In Flight',
    reason: 'Gate Congestion',
    scheduledTime: '08:30',
    predictedTime: '08:53',
    factors: { crosswind: 0.23, gateOccupancy: 0.17, routeDelay: 0.14 },
    scorePayload: {
      flight_id: 'EK230',
      scheduled_departure: '2024-04-01T08:30:00Z',
      scheduled_arrival: '2024-04-01T12:30:00Z',
      weather: { wind_kts: 18, visibility_km: 6 },
      gate: 'A12',
      atc: 'ground hold extension',
    },
  },
  {
    id: 'BA115',
    origin: 'LHR',
    destination: 'JFK',
    delayProb: 0.45,
    predictedDelay: 12,
    status: 'Boarding',
    reason: 'Minor Weather',
    scheduledTime: '10:15',
    predictedTime: '10:27',
    factors: { crosswind: 0.12, gateOccupancy: 0.08, routeDelay: 0.1 },
    scorePayload: {
      flight_id: 'BA115',
      scheduled_departure: '2024-04-01T10:15:00Z',
      scheduled_arrival: '2024-04-01T14:45:00Z',
      weather: { wind_kts: 12, visibility_km: 8 },
      gate: 'B05',
      atc: 'metering in effect',
    },
  },
  {
    id: 'SQ006',
    origin: 'SIN',
    destination: 'LHR',
    delayProb: 0.92,
    predictedDelay: 45,
    status: 'Delayed',
    reason: 'ATC Flow Control',
    scheduledTime: '22:45',
    predictedTime: '23:30',
    factors: { crosswind: 0.35, gateOccupancy: 0.28, routeDelay: 0.29 },
    scorePayload: {
      flight_id: 'SQ006',
      scheduled_departure: '2024-04-01T22:45:00Z',
      scheduled_arrival: '2024-04-02T05:15:00Z',
      weather: { wind_kts: 22, visibility_km: 5 },
      gate: 'C18',
      atc: 'holding pattern',
    },
  },
  {
    id: 'AA501',
    origin: 'DXB',
    destination: 'LAX',
    delayProb: 0.32,
    predictedDelay: 8,
    status: 'On Time',
    reason: 'Normal Operations',
    scheduledTime: '14:00',
    predictedTime: '14:08',
    factors: { crosswind: 0.08, gateOccupancy: 0.05, routeDelay: 0.06 },
    scorePayload: {
      flight_id: 'AA501',
      scheduled_departure: '2024-04-01T14:00:00Z',
      scheduled_arrival: '2024-04-01T22:30:00Z',
      weather: { wind_kts: 8, visibility_km: 10 },
      gate: 'D07',
      atc: 'normal operations',
    },
  },
  {
    id: 'LH720',
    origin: 'FRA',
    destination: 'NRT',
    delayProb: 0.55,
    predictedDelay: 18,
    status: 'Scheduled',
    reason: 'Weather Pattern',
    scheduledTime: '16:30',
    predictedTime: '16:48',
    factors: { crosswind: 0.15, gateOccupancy: 0.12, routeDelay: 0.13 },
    scorePayload: {
      flight_id: 'LH720',
      scheduled_departure: '2024-04-01T16:30:00Z',
      scheduled_arrival: '2024-04-02T02:10:00Z',
      weather: { wind_kts: 14, visibility_km: 7 },
      gate: 'E11',
      atc: 'sequencing program',
    },
  }
];

const mockAlerts = [
  {
    id: 'ALERT001',
    flight: 'SQ006',
    cause: 'ATC Flow Control - Heavy traffic in airspace',
    probability: 92,
    timestamp: '2 minutes ago'
  },
  {
    id: 'ALERT002',
    flight: 'EK230',
    cause: 'Gate Congestion - Multiple departures delayed',
    probability: 78,
    timestamp: '5 minutes ago'
  },
  {
    id: 'ALERT003',
    flight: 'BA115',
    cause: 'Weather System - Storm approaching airport',
    probability: 45,
    timestamp: '8 minutes ago'
  }
];

const Dashboard = () => {
  const [flights, setFlights] = useState(mockFlights);
  const [selectedFlightId, setSelectedFlightId] = useState(mockFlights[0]?.id ?? null);
  const [alerts, setAlerts] = useState(mockAlerts);
  const [adminOpen, setAdminOpen] = useState(false);
  const [scoreDetails, setScoreDetails] = useState(null);
  const [insightsText, setInsightsText] = useState('');
  const [loadingFlights, setLoadingFlights] = useState(false);
  const [loadingScore, setLoadingScore] = useState(false);
  const [apiError, setApiError] = useState(null);
  const navigate = useNavigate();
  const location = useLocation();
  const currentPath = location.pathname;

  const selectedFlight = useMemo(
    () => flights.find((flight) => flight.id === selectedFlightId) || flights[0] || null,
    [flights, selectedFlightId]
  );

  useEffect(() => {
    let active = true;

    async function hydrateFromBackend() {
      setLoadingFlights(true);
      const [flightResult, insightsResult] = await Promise.allSettled([
        fetchFlights(),
        getInsights(),
      ]);
      if (!active) {
        return;
      }

      if (flightResult.status === 'fulfilled' && Array.isArray(flightResult.value)) {
        setFlights((prev) => {
          const flightMap = new Map(prev.map((flight) => [flight.id, flight]));
          flightResult.value.forEach((item) => {
            const id = item.flight_id || item.id;
            if (!id) return;
            const existing = flightMap.get(id) || {
              id,
              origin: item.origin || '—',
              destination: item.dest || item.destination || '—',
              delayProb: typeof item.delay_prob === 'number' ? item.delay_prob : 0,
              predictedDelay: 0,
              status: item.status || 'Scheduled',
              reason: 'Awaiting model analysis',
              scheduledTime: '—',
              predictedTime: '—',
              factors: DEFAULT_FACTORS,
              scorePayload: buildDefaultPayload(id),
            };
            const baseDelay =
              typeof item.delay_prob === 'number' ? item.delay_prob : existing.delayProb;
            flightMap.set(id, {
              ...existing,
              origin: item.origin ?? existing.origin,
              destination: item.dest ?? item.destination ?? existing.destination,
              delayProb: baseDelay,
              predictedDelay: Math.round(baseDelay * 40),
              status: item.status ?? existing.status,
            });
          });
          return Array.from(flightMap.values());
        });
        setSelectedFlightId((prev) => prev || (flightResult.value[0]?.flight_id ?? flightResult.value[0]?.id ?? null));
      } else if (flightResult.status === 'rejected') {
        const reason =
          flightResult.reason?.message || 'Unable to load flights from backend';
        setApiError(reason);
      }

      if (insightsResult.status === 'fulfilled') {
        const payload = insightsResult.value;
        setInsightsText(
          typeof payload === 'string'
            ? payload
            : payload?.explanation || payload?.message || 'Insights service available'
        );
      } else if (insightsResult.status === 'rejected') {
        setInsightsText('Langflow insights offline - showing cached copy.');
      }

      setLoadingFlights(false);
    }

    hydrateFromBackend().catch((err) => {
      if (!active) return;
      setApiError(err.message || 'Backend unreachable');
      setLoadingFlights(false);
    });

    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    const interval = setInterval(() => {
      setAlerts((prev) => {
        const newAlert = prev[prev.length - 1];
        return [newAlert, ...prev.slice(0, -1)];
      });
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (!selectedFlight?.scorePayload) {
      setScoreDetails(null);
      return;
    }

    let active = true;
    setLoadingScore(true);

    const payload = {
      ...selectedFlight.scorePayload,
      flight_id: selectedFlight.scorePayload.flight_id || selectedFlight.id,
    };

    scoreFlight(payload)
      .then((result) => {
        if (!active) return;
        setScoreDetails(result);
        setFlights((prev) =>
          prev.map((flight) =>
            flight.id === selectedFlight.id
              ? {
                  ...flight,
                  delayProb: result.delay_prob ?? flight.delayProb,
                  predictedDelay: result.predicted_delay_minutes ?? flight.predictedDelay,
                  factors: shapToFactors(result.shap) || flight.factors,
                }
              : flight
          )
        );
      })
      .catch((err) => {
        if (!active) return;
        setApiError(err.message || 'Failed to score flight');
        setScoreDetails(null);
      })
      .finally(() => {
        if (active) setLoadingScore(false);
      });

    return () => {
      active = false;
    };
  }, [selectedFlight?.id, selectedFlight?.scorePayload]);

  const getProbabilityClass = (prob) => {
    if (prob < 0.4) return 'green';
    if (prob < 0.7) return 'yellow';
    return 'red';
  };

  const getFlightProbability = (flight) => {
    return Math.round(flight.delayProb * 100);
  };

  const detailProbability =
    scoreDetails?.delay_prob ?? selectedFlight?.delayProb ?? 0;
  const detailDelayMinutes =
    scoreDetails?.predicted_delay_minutes ?? selectedFlight?.predictedDelay ?? 0;

  const factorValues = useMemo(() => {
    if (scoreDetails?.shap) {
      return {
        ...DEFAULT_FACTORS,
        ...shapToFactors(scoreDetails.shap),
      };
    }
    return selectedFlight?.factors || DEFAULT_FACTORS;
  }, [scoreDetails, selectedFlight]);

  const explanationText =
    scoreDetails?.explanation ||
    'Model explanation pending. Check Langflow or Ollama connectivity if this persists.';

  const insightsCopy =
    insightsText ||
    'Weather-related congestion increased average delay risk by 18% across major hubs this morning. ATC flow control measures are in effect at 5 international airports. System recommends prioritizing gate allocation for high-risk flights and pre-notifying crews of potential delays beyond 20 minutes.';

  const statusBannerStyle = {
    background: 'rgba(182, 255, 43, 0.06)',
    border: '1px solid rgba(182, 255, 43, 0.25)',
    color: '#B6FF2B',
    padding: '0.75rem 1rem',
    borderRadius: '6px',
    marginBottom: '1rem',
    fontSize: '0.85rem',
    letterSpacing: '0.3px',
  };

  const errorBannerStyle = {
    ...statusBannerStyle,
    background: 'rgba(255, 100, 100, 0.1)',
    border: '1px solid rgba(255, 100, 100, 0.35)',
    color: '#ff7a7a',
  };

  return (
    <DashboardContainer id="dashboard">
      <HeaderNav>
        <NavContent>
          <Link to="/" style={{ textDecoration: 'none' }}>
            <div className="nav-logo">PreFlight AI</div>
          </Link>
          <div className="nav-tabs">
            <Link to="/dashboard" style={{ textDecoration: 'none', color: 'inherit' }}>
              <span className={currentPath === '/dashboard' ? 'active' : ''}>Dashboard</span>
            </Link>
            <Link to="/alerts" style={{ textDecoration: 'none', color: 'inherit' }}>
              <span className={currentPath === '/alerts' ? 'active' : ''}>Alerts</span>
            </Link>
            <Link to="/analytics" style={{ textDecoration: 'none', color: 'inherit' }}>
              <span className={currentPath === '/analytics' ? 'active' : ''}>Analytics</span>
            </Link>
            <Link to="/insights" style={{ textDecoration: 'none', color: 'inherit' }}>
              <span className={currentPath === '/insights' ? 'active' : ''}>Insights</span>
            </Link>
            <Link to="/system" style={{ textDecoration: 'none', color: 'inherit' }}>
              <span className={currentPath === '/system' ? 'active' : ''}>System</span>
            </Link>
          </div>
          <div className="nav-actions">
            <button onClick={() => navigate('/settings')}>Settings</button>
            <button onClick={() => navigate('/profile')}>Profile</button>
          </div>
        </NavContent>
      </HeaderNav>

      <MainContent>
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.6 }}
        >
          <KPIGrid>
            <KPICard whileHover={{ y: -5 }}>
              <div className="kpi-label">Flights Analyzed</div>
              <div className="kpi-value">247</div>
              <div className="kpi-change">+12 today</div>
            </KPICard>

            <KPICard whileHover={{ y: -5 }}>
              <div className="kpi-label">Avg Predicted Delay</div>
              <div className="kpi-value">21 min</div>
              <div className="kpi-change">↑ 3% from baseline</div>
            </KPICard>

            <KPICard whileHover={{ y: -5 }}>
              <div className="kpi-label">Prediction Accuracy</div>
              <div className="kpi-value">94.2%</div>
              <div className="kpi-change">Model: LSTM-XGBoost</div>
            </KPICard>

            <KPICard whileHover={{ y: -5 }}>
              <div className="kpi-label">Alerts Triggered</div>
              <div className="kpi-value">18</div>
              <div className="kpi-change">3 critical</div>
            </KPICard>
          </KPIGrid>
        </motion.div>

        <FlightsSection>
          <div>
            {apiError && (
              <div style={errorBannerStyle}>{apiError}</div>
            )}
            {loadingFlights && !apiError && (
              <div style={statusBannerStyle}>Syncing flights with backend…</div>
            )}
            <FlightsTable>
              <SearchBar>
                <input
                  type="text"
                  placeholder="Search by flight ID, airport, or gate..."
                />
              </SearchBar>

              <div className="table-header">
                <div>Flight ID</div>
                <div>Route</div>
                <div>Delay Prob</div>
                <div className="predicted-delay">Predicted Delay</div>
                <div>Status</div>
              </div>

              <div className="table-body">
                {flights.length === 0 ? (
                  <div style={{ padding: '1.2rem', color: 'rgba(255, 255, 255, 0.6)' }}>
                    No flights available. Try again shortly.
                  </div>
                ) : (
                  flights.map((flight, idx) => (
                    <motion.div
                      key={flight.id}
                      className={`table-row ${selectedFlight?.id === flight.id ? 'selected' : ''}`}
                      onClick={() => setSelectedFlightId(flight.id)}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: idx * 0.05 }}
                      whileHover={{ backgroundColor: 'rgba(182, 255, 43, 0.08)' }}
                    >
                      <div className="flight-id">{flight.id}</div>
                      <div className="route">
                        {flight.origin} → {flight.destination}
                      </div>
                      <div
                        className={`delay-probability ${getProbabilityClass(flight.delayProb)}`}
                      >
                        {getFlightProbability(flight)}%
                      </div>
                      <div className="predicted-delay">{flight.predictedDelay} min</div>
                      <div className="status">{flight.status}</div>
                    </motion.div>
                  ))
                )}
              </div>
            </FlightsTable>
          </div>

          <FlightDetailPanel
            initial={{ opacity: 0, x: 10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5 }}
            key={selectedFlight?.id || 'detail-panel'}
          >
            {selectedFlight ? (
              <>
                <div className="detail-title">{selectedFlight.id} Details</div>

                <div className="detail-row">
                  <label>Route</label>
                  <span>
                    {selectedFlight.origin} → {selectedFlight.destination}
                  </span>
                </div>

                <div className="detail-row">
                  <label>Scheduled Departure</label>
                  <span>{selectedFlight.scheduledTime}</span>
                </div>

                <div className="detail-row">
                  <label>Status</label>
                  <span>{selectedFlight.status}</span>
                </div>

                <div className="detail-row">
                  <label>Predicted Departure</label>
                  <span>{selectedFlight.predictedTime}</span>
                </div>

                <div className="detail-row">
                  <label>Delay Probability</label>
                  <span>{Math.round(detailProbability * 100)}%</span>
                </div>

                <div className="detail-row">
                  <label>Predicted Delay</label>
                  <span>{Math.round(detailDelayMinutes)} min</span>
                </div>

                <div className="explanation">
                  <div className="exp-title">
                    AI Explanation {loadingScore ? '(updating...)' : ''}
                  </div>
                  <div>
                    {scoreDetails?.explanation
                      ? explanationText
                      : `${selectedFlight.reason} is the primary delay driver. High winds and gate congestion are increasing delay risk. System recommends proactive crew notification.`}
                  </div>
                </div>

                <div className="contributing-factors">
                  <div className="factors-title">Top Contributing Factors</div>
                  <div className="factor-item">
                    <div className="factor-name">Crosswind Impact</div>
                    <div className="factor-bar">
                      <div
                        className="factor-fill"
                        style={{ width: `${factorValues.crosswind * 100}%` }}
                      ></div>
                    </div>
                    <div className="factor-value">
                      {Math.round(factorValues.crosswind * 100)}%
                    </div>
                  </div>
                  <div className="factor-item">
                    <div className="factor-name">Gate Occupancy</div>
                    <div className="factor-bar">
                      <div
                        className="factor-fill"
                        style={{ width: `${factorValues.gateOccupancy * 100}%` }}
                      ></div>
                    </div>
                    <div className="factor-value">
                      {Math.round(factorValues.gateOccupancy * 100)}%
                    </div>
                  </div>
                  <div className="factor-item">
                    <div className="factor-name">Route Delay</div>
                    <div className="factor-bar">
                      <div
                        className="factor-fill"
                        style={{ width: `${factorValues.routeDelay * 100}%` }}
                      ></div>
                    </div>
                    <div className="factor-value">
                      {Math.round(factorValues.routeDelay * 100)}%
                    </div>
                  </div>
                </div>

                <button className="notify-button">Notify Crew</button>
              </>
            ) : (
              <div style={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                Select a flight to view prediction details.
              </div>
            )}
          </FlightDetailPanel>
        </FlightsSection>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          <InsightsSection>
            <div className="insights-title">AI Insights</div>
            <div className="insights-text">{insightsCopy}</div>

            <div className="charts-container">
              <ChartContainer>
                <div className="chart-title">Delay Trend (Last 6 Hours)</div>
                <div style={{ height: '150px', background: 'rgba(182, 255, 43, 0.1)', borderRadius: '6px', display: 'flex', alignItems: 'flex-end', justifyContent: 'space-around', padding: '10px' }}>
                  {[15, 18, 22, 19, 25, 21].map((val, idx) => (
                    <div key={idx} style={{ height: `${val * 2}%`, background: '#B6FF2B', borderRadius: '4px 4px 0 0', width: '12%' }}></div>
                  ))}
                </div>
              </ChartContainer>

              <ChartContainer>
                <div className="chart-title">Delay Causes Breakdown</div>
                <div style={{ height: '150px', background: 'rgba(182, 255, 43, 0.1)', borderRadius: '6px', padding: '10px', color: 'rgba(255, 255, 255, 0.7)', fontSize: '0.9rem' }}>
                  <div style={{ marginBottom: '8px' }}>🟢 Weather: 35%</div>
                  <div style={{ marginBottom: '8px' }}>🟢 Gate: 28%</div>
                  <div style={{ marginBottom: '8px' }}>🟢 ATC: 22%</div>
                  <div>🟢 Other: 15%</div>
                </div>
              </ChartContainer>
            </div>
          </InsightsSection>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
        >
          <AlertsSection>
            <div className="alerts-title">Real-Time Alerts</div>
            <div className="alerts-list">
              {alerts.map((alert, idx) => (
                <motion.div
                  key={alert.id}
                  className="alert-card"
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: idx * 0.05 }}
                >
                  <div className="alert-header">
                    <div className="flight-id">{alert.flight}</div>
                    <div className="timestamp">{alert.timestamp}</div>
                  </div>
                  <div className="alert-content">{alert.cause}</div>
                  <div style={{ fontSize: '0.85rem', color: 'rgba(255, 100, 100, 0.8)', marginBottom: '0.8rem' }}>
                    Probability: {alert.probability}%
                  </div>
                  <div className="alert-actions">
                    <button>Acknowledge</button>
                    <button className="escalate">Escalate</button>
                  </div>
                </motion.div>
              ))}
            </div>
          </AlertsSection>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.4 }}
        >
          <AdminPanel>
            <div className="admin-title">
              Admin Control Panel
              <button className="toggle-btn" onClick={() => setAdminOpen(!adminOpen)}>
                {adminOpen ? 'Collapse' : 'Expand'}
              </button>
            </div>

            {adminOpen && (
              <div className="admin-content">
                <div className="admin-item">
                  <div className="item-label">Model Type</div>
                  <select>
                    <option>LSTM-XGBoost</option>
                    <option>Prophet</option>
                    <option>XGBoost</option>
                  </select>
                </div>

                <div className="admin-item">
                  <div className="item-label">Backend Status</div>
                  <div className="item-value">🟢 Online</div>
                </div>

                <div className="admin-item">
                  <div className="item-label">FastAPI</div>
                  <div className="item-value">✓ Connected</div>
                </div>

                <div className="admin-item">
                  <div className="item-label">Langflow</div>
                  <div className="item-value">✓ Connected</div>
                </div>

                <div className="admin-item">
                  <div className="item-label">n8n</div>
                  <div className="item-value">✓ Active</div>
                </div>

                <div className="admin-item">
                  <div className="item-label">Last Retrain</div>
                  <div className="item-value">2h ago</div>
                </div>
              </div>
            )}
          </AdminPanel>
        </motion.div>
      </MainContent>

      <FooterSection>
        <div className="footer-text">PreFlight AI © 2025 — Built with Langflow, n8n, and local open-source AI.</div>
        <div className="footer-links">
          <a href="https://github.com" target="_blank" rel="noopener noreferrer">GitHub</a>
          <a href="https://docs.preflight.ai" target="_blank" rel="noopener noreferrer">Docs</a>
          <a href="mailto:contact@preflight.ai">Contact</a>
        </div>
      </FooterSection>
    </DashboardContainer>
  );
};

export default Dashboard;

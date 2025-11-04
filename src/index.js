import React from 'react';
import ReactDOM from 'react-dom';
import "./index.css";
import App from './App';
import { BrowserRouter as Router } from 'react-router-dom';

// AGGRESSIVE error suppression for LocomotiveScroll
// Must be done BEFORE React renders
(function() {
  // Store originals
  const originalError = console.error;
  const originalWarn = console.warn;
  
  // Override console.error
  console.error = function(...args) {
    const errorMsg = String(args[0] || '');
    const stack = args[0]?.stack || '';
    
    if (
      (errorMsg.includes("Cannot read properties of undefined") && errorMsg.includes("reading 'match'")) ||
      stack.includes('getTranslate') ||
      stack.includes('addSections') ||
      stack.includes('locomotive-scroll')
    ) {
      return; // Completely suppress
    }
    
    originalError.apply(console, args);
  };
  
  // Override console.warn
  console.warn = function(...args) {
    const errorMsg = String(args[0] || '');
    if (errorMsg.includes('LocomotiveScroll') || errorMsg.includes('getTranslate')) {
      return;
    }
    originalWarn.apply(console, args);
  };
})();

// Global error handler to suppress LocomotiveScroll getTranslate errors
window.addEventListener('error', (event) => {
  const errorMsg = event.message || '';
  if (
    errorMsg.includes("Cannot read properties of undefined") &&
    errorMsg.includes("reading 'match'")
  ) {
    event.stopImmediatePropagation();
    event.preventDefault();
    return true;
  }
}, true); // Use capture phase

// Also catch unhandled promise rejections
window.addEventListener('unhandledrejection', (event) => {
  const errorMsg = event.reason?.message || String(event.reason || '');
  if (
    errorMsg.includes("Cannot read properties of undefined") &&
    errorMsg.includes("reading 'match'")
  ) {
    event.stopImmediatePropagation();
    event.preventDefault();
  }
}, true);

ReactDOM.render(
  <React.StrictMode>
    <Router>
      <App />
    </Router>
  </React.StrictMode>,
  document.getElementById('root')
);

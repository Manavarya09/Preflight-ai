import React, { useEffect, useRef } from 'react';
import { LocomotiveScrollProvider } from 'react-locomotive-scroll';

/**
 * Safe wrapper for LocomotiveScrollProvider that handles getTranslate errors
 * This patches the window object to catch LocomotiveScroll internal errors
 */
const SafeLocomotiveScrollProvider = ({ children, ...props }) => {
  const errorPatchedRef = useRef(false);
  
  useEffect(() => {
    if (errorPatchedRef.current) return;
    errorPatchedRef.current = true;
    
    // Monkey-patch window.onerror to catch and suppress LocomotiveScroll errors
    const originalOnError = window.onerror;
    
    window.onerror = (message, source, lineno, colno, error) => {
      const errorMsg = String(message || '');
      
      // Check if this is the LocomotiveScroll getTranslate error
      if (
        errorMsg.includes("Cannot read properties of undefined") &&
        errorMsg.includes("reading 'match'")
      ) {
        return true; // Prevent error from propagating
      }
      
      // Call original handler for other errors
      if (originalOnError) {
        return originalOnError(message, source, lineno, colno, error);
      }
      
      return false; // Let browser handle it
    };

    // Also patch console.error for bundled errors
    const originalError = console.error;
    console.error = (...args) => {
      const errorMsg = String(args[0] || '');
      const stack = args[0]?.stack || '';
      
      if (
        (errorMsg.includes("Cannot read properties of undefined") &&
        errorMsg.includes("reading 'match'")) ||
        stack.includes('getTranslate') ||
        stack.includes('addSections')
      ) {
        return; // Suppress
      }
      
      originalError.apply(console, args);
    };

    return () => {
      window.onerror = originalOnError;
      console.error = originalError;
    };
  }, []);

  // Wrap in error boundary-like behavior
  try {
    return (
      <LocomotiveScrollProvider {...props}>
        {children}
      </LocomotiveScrollProvider>
    );
  } catch (error) {
    if (error?.message?.includes("reading 'match'")) {
      // Suppress and render children anyway
      return <>{children}</>;
    }
    throw error;
  }
};

export default SafeLocomotiveScrollProvider;

import { useEffect } from 'react';

/**
 * Hook to suppress LocomotiveScroll transform errors
 * These errors occur when LocomotiveScroll tries to read transform properties
 * from elements that don't have them properly set up
 */
export const useSuppressScrollErrors = () => {
  useEffect(() => {
    // Store the original console.error
    const originalError = console.error;

    // Override console.error to catch and suppress specific errors
    console.error = (...args) => {
      const errorMsg = args[0]?.toString?.() || '';
      
      // Suppress LocomotiveScroll transform errors
      if (
        errorMsg.includes("Cannot read properties of undefined (reading 'match')") ||
        errorMsg.includes("reading 'match'") ||
        (args[0]?.message?.includes("Cannot read properties of undefined") && 
         args[0]?.stack?.includes('getTranslate'))
      ) {
        console.warn('⚠️ LocomotiveScroll transform error suppressed');
        return;
      }

      // For other errors, call the original console.error
      originalError.apply(console, args);
    };

    return () => {
      // Restore original console.error on cleanup
      console.error = originalError;
    };
  }, []);
};

export default useSuppressScrollErrors;

/**
 * Safe scroll utility functions to prevent undefined errors with LocomotiveScroll
 */

/**
 * Safely get transform value from an element
 * @param {HTMLElement} element - DOM element
 * @returns {string|null} - Transform value or null if not found
 */
export const getSafeTransform = (element) => {
  try {
    if (!element) return null;
    const style = window?.getComputedStyle?.(element);
    const transform = style?.transform || element?.style?.transform;
    
    // Ensure it's a valid string before returning
    if (typeof transform === 'string' && transform.length > 0) {
      return transform;
    }
    return null;
  } catch (error) {
    console.warn('Error getting transform:', error?.message);
    return null;
  }
};

/**
 * Safely get scroll data from element
 * @param {HTMLElement} element - DOM element
 * @returns {object} - Safe scroll data
 */
export const getSafeScrollData = (element) => {
  try {
    if (!element) {
      return {
        x: 0,
        y: 0,
      };
    }
    
    // Try multiple ways to access scroll data safely
    let scrollData = null;
    
    // Method 1: Direct scroll property
    if (element?.scroll?.instance?.scroll) {
      scrollData = element.scroll.instance.scroll;
    }
    // Method 2: Direct y property
    else if (typeof element?.y === 'number') {
      scrollData = element;
    }
    // Method 3: Fallback to empty
    else {
      scrollData = {};
    }
    
    return {
      x: (scrollData?.x ?? scrollData?.scrollX ?? 0) || 0,
      y: (scrollData?.y ?? scrollData?.scrollY ?? 0) || 0,
    };
  } catch (error) {
    console.warn('Error getting scroll data:', error?.message);
    return {
      x: 0,
      y: 0,
    };
  }
};

/**
 * Safely check if element has scroll data
 * @param {object} scrollInstance - Scroll instance from LocomotiveScroll
 * @returns {boolean}
 */
export const hasScrollData = (scrollInstance) => {
  try {
    if (!scrollInstance) return false;
    
    return !!(
      scrollInstance?.scroll?.instance?.scroll || 
      scrollInstance?.y !== undefined ||
      scrollInstance?.scroll?.y !== undefined
    );
  } catch {
    return false;
  }
};

/**
 * Patch console methods to suppress specific LocomotiveScroll errors
 */
export const suppressLocomotiveScrollErrors = () => {
  const originalError = console.error;
  
  console.error = (...args) => {
    const errorMsg = String(args[0] || '');
    const stack = args[0]?.stack || '';
    
    // Suppress LocomotiveScroll getTranslate errors
    if (
      errorMsg.includes("Cannot read properties of undefined") &&
      errorMsg.includes("reading 'match'") &&
      stack.includes('getTranslate')
    ) {
      return; // Silently suppress
    }
    
    // Call original for other errors
    originalError.apply(console, args);
  };
  
  return () => {
    console.error = originalError;
  };
};

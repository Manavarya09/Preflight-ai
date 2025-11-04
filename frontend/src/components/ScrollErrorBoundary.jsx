import React from 'react';

class ScrollErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error) {
    // Check if this is the LocomotiveScroll transform error
    if (error?.message?.includes('reading \'match\'') || error?.message?.includes('Cannot read properties of undefined')) {
      console.warn('Caught LocomotiveScroll transform error - suppressing');
      return { hasError: false }; // Don't crash, just log it
    }
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    // Log the error but don't propagate if it's the scroll transform error
    if (error?.message?.includes('reading \'match\'')) {
      console.warn('LocomotiveScroll error caught and suppressed:', error.message);
    } else {
      console.error('ScrollErrorBoundary caught error:', error, errorInfo);
    }
  }

  render() {
    if (this.state.hasError) {
      return <div>Something went wrong. Please refresh the page.</div>;
    }

    return this.props.children;
  }
}

export default ScrollErrorBoundary;

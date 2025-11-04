import React from 'react';

class LocomotiveScrollErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error) {
    // Check if this is the LocomotiveScroll transform error
    const errorMsg = error?.message || '';
    if (
      errorMsg.includes("Cannot read properties of undefined") &&
      errorMsg.includes("reading 'match'")
    ) {
      // Don't show error UI, just suppress it
      return { hasError: false };
    }
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    const errorMsg = error?.message || '';
    if (
      errorMsg.includes("Cannot read properties of undefined") &&
      errorMsg.includes("reading 'match'")
    ) {
      // Suppress this error completely
      return;
    }
    // Log other errors
    console.error('Error caught by boundary:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return <div>Something went wrong. Please refresh the page.</div>;
    }

    return this.props.children;
  }
}

export default LocomotiveScrollErrorBoundary;

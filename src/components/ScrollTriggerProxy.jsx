// To use gsap with locomotive scroll, we have to use scroller proxy provided by gsap
import gsap from 'gsap';
import ScrollTrigger from 'gsap/ScrollTrigger';
import { useEffect } from 'react';
import { useLocomotiveScroll } from 'react-locomotive-scroll';
import { getSafeTransform, getSafeScrollData } from '../utils/scrollUtils';

const ScrollTriggerProxy = () => {
  // first let's get instance of locomotive scroll

  const { scroll } = useLocomotiveScroll();
  // Register scroll trigger plugin
  gsap.registerPlugin(ScrollTrigger);

  useEffect(() => {
    if (scroll) {
      const element = scroll?.el; // locomotive scrolling element, in our case it's app (main)

      // Guard check: ensure element exists before proceeding
      if (!element) {
        console.warn('LocomotiveScroll element not found');
        return;
      }

      scroll.on('scroll', ScrollTrigger.update); // on scroll of locomotive, update scrolltrigger

      //  let's use scroller proxy
      ScrollTrigger.scrollerProxy(element, {
        scrollTop(value) {
          if (arguments.length) {
            return scroll.scrollTo(value, 0, 0);
          }
          // Safely get scroll Y value
          const scrollData = getSafeScrollData(scroll);
          return scrollData.y ?? 0;
        }, // we don't have to define a scrollLeft because we're only scrolling vertically.
        getBoundingClientRect() {
          return {
            top: 0,
            left: 0,
            width: window.innerWidth,
            height: window.innerHeight,
          };
        },
        // LocomotiveScroll handles things completely differently on mobile devices - it doesn't even transform the container at all! So to get the correct behavior and avoid jitters, we should pin things with position: fixed on mobile. We sense it by checking to see if there's a transform applied to the container (the LocomotiveScroll-controlled element).
        pinType: getSafeTransform(element) ? 'transform' : 'fixed',
      });
    }

    return () => {
      ScrollTrigger.addEventListener('refresh', () =>
        scroll?.update?.()
      );
      ScrollTrigger.refresh();
    };
  }, [scroll]);

  return null;
};

export default ScrollTriggerProxy;

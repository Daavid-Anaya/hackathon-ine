import { useEffect, useRef } from 'react';

export function useScrollReveal() {
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (!ref.current || !window.IntersectionObserver || matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    const observer = new IntersectionObserver(entries => {
      for (const entry of entries) {
        if (entry.isIntersecting) {
          entry.target.classList.add('revealed');
          observer.unobserve(entry.target);
        }
      }
    }, { threshold: 0.08 });
    ref.current.querySelectorAll('[data-reveal]').forEach(element => observer.observe(element));
    return () => observer.disconnect();
  }, []);
  return ref;
}

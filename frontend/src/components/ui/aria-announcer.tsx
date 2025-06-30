import { useEffect } from 'react';

export function AriaAnnouncer({ message }: { message: string }) {
  useEffect(() => {
    if (message) {
      const liveRegion = document.getElementById('aria-live-region');
      if (liveRegion) {
        liveRegion.textContent = '';
        setTimeout(() => {
          liveRegion.textContent = message;
        }, 100);
      }
    }
  }, [message]);

  return (
    <div id="aria-live-region" aria-live="polite" aria-atomic="true" style={{ position: 'absolute', left: -9999, top: 'auto', width: 1, height: 1, overflow: 'hidden' }} />
  );
}

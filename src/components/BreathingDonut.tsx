import { useEffect, useRef } from 'react';

interface BreathingDonutProps {
  isActive: boolean;
  durationSeconds: number;
  onComplete: () => void;
}

export default function BreathingDonut({ isActive, durationSeconds, onComplete }: BreathingDonutProps) {
  const animationRef = useRef<number | null>(null);
  const startTimeRef = useRef<number>(0);
  const audioContextRef = useRef<AudioContext | null>(null);
  const hasPlayedChimeRef = useRef(false);

  useEffect(() => {
    if (!isActive) return;

    // Reset refs
    hasPlayedChimeRef.current = false;
    startTimeRef.current = performance.now();
    
    // Create audio context for the chime
    const audioContext = new (window.AudioContext || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext)();
    audioContextRef.current = audioContext;

    const breathe = (timestamp: number) => {
      if (!isActive) return;

      const elapsed = timestamp - startTimeRef.current;
      const cycleDuration = 8000; // 8 seconds per breath
      const progress = (elapsed % cycleDuration) / cycleDuration;
      
      // Sine wave for smooth breathing: 0.7 → 1.3 → 0.7
      const scale = 0.7 + 0.6 * (0.5 - 0.5 * Math.cos(2 * Math.PI * progress));
      
      const donut = document.getElementById('breathing-donut');
      if (donut) {
        donut.style.transform = `scale(${scale})`;
      }

      // Check if silence duration is complete
      if (elapsed >= durationSeconds * 1000 && !hasPlayedChimeRef.current) {
        hasPlayedChimeRef.current = true;
        playChime(audioContext);
        onComplete();
        return;
      }

      animationRef.current = requestAnimationFrame(breathe);
    };

    animationRef.current = requestAnimationFrame(breathe);

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
      if (audioContextRef.current) {
        audioContextRef.current.close();
      }
    };
  }, [isActive, durationSeconds, onComplete]);

  function playChime(audioContext: AudioContext) {
    // 528Hz sine wave - the "healing frequency"
    const oscillator = audioContext.createOscillator();
    const gainNode = audioContext.createGain();
    
    oscillator.type = 'sine';
    oscillator.frequency.setValueAtTime(528, audioContext.currentTime);
    
    // Soft attack and release for a gentle chime
    gainNode.gain.setValueAtTime(0, audioContext.currentTime);
    gainNode.gain.linearRampToValueAtTime(0.3, audioContext.currentTime + 0.1);
    gainNode.gain.exponentialRampToValueAtTime(0.001, audioContext.currentTime + 2);
    
    oscillator.connect(gainNode);
    gainNode.connect(audioContext.destination);
    
    oscillator.start(audioContext.currentTime);
    oscillator.stop(audioContext.currentTime + 2);
  }

  if (!isActive) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-silence-blue transition-colors duration-700">
      <div className="text-center">
        <div
          id="breathing-donut"
          className="w-32 h-32 rounded-full bg-gold mx-auto mb-6 shadow-lg"
          style={{
            boxShadow: '0 0 60px rgba(201, 148, 74, 0.4)',
            transform: 'scale(0.7)',
          }}
        />
        <p className="text-gold/70 text-lg">Breathe...</p>
      </div>
    </div>
  );
}

import { Box, useColorModeValue } from '@chakra-ui/react';
import { useEffect, useRef } from 'react';

export function ParticleBackground() {
  const containerRef = useRef<HTMLDivElement>(null);
  const particleColor = useColorModeValue('rgba(0, 123, 255, 0.3)', 'rgba(96, 165, 250, 0.3)');

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const particleCount = 20;
    const particles: HTMLDivElement[] = [];

    for (let i = 0; i < particleCount; i++) {
      const particle = document.createElement('div');
      particle.style.cssText = `
        position: absolute;
        width: ${4 + Math.random() * 6}px;
        height: ${4 + Math.random() * 6}px;
        background: ${particleColor};
        border-radius: 50%;
        left: ${Math.random() * 100}%;
        animation: floatParticle ${15 + Math.random() * 10}s infinite ease-in-out;
        animation-delay: ${Math.random() * 15}s;
        opacity: ${0.2 + Math.random() * 0.3};
      `;
      container.appendChild(particle);
      particles.push(particle);
    }

    return () => {
      particles.forEach((p) => p.remove());
    };
  }, [particleColor]);

  return (
    <>
      <style>
        {`
          @keyframes floatParticle {
            0%, 100% {
              transform: translateY(100vh) rotate(0deg);
              opacity: 0;
            }
            10% {
              opacity: 1;
            }
            90% {
              opacity: 1;
            }
            100% {
              transform: translateY(-100vh) rotate(720deg);
              opacity: 0;
            }
          }
        `}
      </style>
      <Box
        ref={containerRef}
        position="fixed"
        top={0}
        left={0}
        right={0}
        bottom={0}
        pointerEvents="none"
        zIndex={0}
        overflow="hidden"
      />
      <Box
        position="fixed"
        top={0}
        left={0}
        right={0}
        bottom={0}
        pointerEvents="none"
        zIndex={0}
        bgGradient={useColorModeValue(
          'linear(135deg, rgba(0, 123, 255, 0.05) 0%, rgba(0, 198, 255, 0.05) 50%, rgba(0, 123, 255, 0.05) 100%)',
          'linear(135deg, rgba(59, 130, 246, 0.08) 0%, rgba(6, 182, 212, 0.08) 50%, rgba(59, 130, 246, 0.08) 100%)'
        )}
        bgSize="400% 400%"
        animation="gradientShift 15s ease infinite"
      />
      <style>
        {`
          @keyframes gradientShift {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
          }
        `}
      </style>
    </>
  );
}

import { Box, Flex, Image, useColorModeValue } from '@chakra-ui/react';
import { motion } from 'framer-motion';

const MotionBox = motion(Box);

export function TypingIndicator() {
  const dotBg = useColorModeValue('blue.400', 'blue.300');
  const containerBg = useColorModeValue('white', 'gray.700');

  return (
    <Flex align="center" gap={3} px={6} py={3}>
      <Flex
        w={8}
        h={8}
        borderRadius="full"
        align="center"
        justify="center"
        bg="linear-gradient(135deg, #3182ce, #00c6ff)"
      >
        <Image src="/ai-icon.png" alt="AI" boxSize="100%" borderRadius="full" />
      </Flex>

      <Flex
        bg={containerBg}
        px={4}
        py={3}
        borderRadius="xl"
        gap={2}
        boxShadow="0 2px 10px rgba(0, 0, 0, 0.05)"
      >
        {[0, 1, 2].map((i) => (
          <MotionBox
            key={i}
            w={2}
            h={2}
            borderRadius="full"
            bg={dotBg}
            animate={{
              y: [-4, 4, -4],
              opacity: [0.4, 1, 0.4],
            }}
            transition={{
              duration: 1.4,
              repeat: Infinity,
              delay: i * 0.2,
              ease: 'easeInOut',
            }}
          />
        ))}
      </Flex>
    </Flex>
  );
}

import {
  Alert,
  AlertDescription,
  AlertTitle,
  Box,
  CloseButton,
  Flex,
  Icon,
  useColorModeValue,
  Wrap,
  WrapItem,
} from '@chakra-ui/react';
import {
  FiAlertTriangle,
  FiCalendar,
  FiEdit3,
  FiStar,
  FiSun,
} from 'react-icons/fi';
import { motion, AnimatePresence } from 'framer-motion';
import { ScheduleAlert } from '../types';

interface AlertBannerProps {
  alerts: ScheduleAlert[];
  onDismiss: (index: number) => void;
}

const MotionBox = motion(Box);

const iconMap: { [key: string]: typeof FiStar } = {
  warning: FiAlertTriangle,
  edit: FiEdit3,
  sun: FiSun,
  calendar: FiCalendar,
  star: FiStar,
};

const colorSchemeMap: { [key: string]: string } = {
  exam: 'red',
  holiday: 'green',
  closed: 'blue',
  event: 'orange',
};

export function AlertBanner({ alerts, onDismiss }: AlertBannerProps) {
  const bgColor = useColorModeValue('white', 'gray.800');

  if (alerts.length === 0) return null;

  return (
    <Box
      bg={bgColor}
      backdropFilter="blur(10px)"
      borderBottom="1px solid"
      borderColor={useColorModeValue('gray.100', 'gray.700')}
      px={4}
      py={3}
    >
      <Wrap spacing={3}>
        <AnimatePresence>
          {alerts.map((alert, index) => (
            <WrapItem key={`${alert.type}-${alert.title}`}>
              <MotionBox
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                transition={{ duration: 0.2 }}
              >
                <Alert
                  status="info"
                  variant="subtle"
                  borderRadius="lg"
                  colorScheme={colorSchemeMap[alert.type]}
                  pr={10}
                >
                  <Flex align="center" gap={3}>
                    <Icon
                      as={iconMap[alert.icon] || FiStar}
                      boxSize={5}
                    />
                    <Box>
                      <AlertTitle fontSize="sm" fontWeight="600">
                        {alert.title}
                      </AlertTitle>
                      <AlertDescription fontSize="xs">
                        {alert.message}
                      </AlertDescription>
                    </Box>
                  </Flex>
                  <CloseButton
                    position="absolute"
                    right={2}
                    top={2}
                    size="sm"
                    onClick={() => onDismiss(index)}
                  />
                </Alert>
              </MotionBox>
            </WrapItem>
          ))}
        </AnimatePresence>
      </Wrap>
    </Box>
  );
}

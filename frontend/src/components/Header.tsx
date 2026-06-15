import {
  Box,
  Flex,
  Heading,
  HStack,
  IconButton,
  Image,
  Tag,
  Text,
  useColorMode,
  useColorModeValue,
} from '@chakra-ui/react';
import {
  FiMoon,
  FiSun,
  FiTrash2,
  FiClock,
  FiLogOut,
} from 'react-icons/fi';
import { User } from 'firebase/auth';
import { ApiStatus } from '../types';

interface HeaderProps {
  user: User;
  apiStatus: ApiStatus;
  onToggleHistory: () => void;
  onClearChat: () => void;
  onLogout: () => void;
}

export function Header({
  user,
  apiStatus,
  onToggleHistory,
  onClearChat,
  onLogout,
}: HeaderProps) {
  const { colorMode, toggleColorMode } = useColorMode();

  const statusColors = {
    online: { bg: 'green.100', color: 'green.600', darkBg: 'green.900', darkColor: 'green.300' },
    offline: { bg: 'red.100', color: 'red.600', darkBg: 'red.900', darkColor: 'red.300' },
    connecting: { bg: 'yellow.100', color: 'yellow.600', darkBg: 'yellow.900', darkColor: 'yellow.300' },
  };

  const statusConfig = statusColors[apiStatus];
  const statusText = {
    online: 'オンライン',
    offline: 'オフライン',
    connecting: '接続中...',
  };

  return (
    <Box
      as="header"
      px={{ base: 3, md: 6 }}
      py={3}
      bg={useColorModeValue('white', 'gray.800')}
      borderBottom="1px solid"
      borderColor={useColorModeValue('gray.200', 'gray.700')}
    >
      <Flex justify="space-between" align="center">
        <HStack spacing={{ base: 2, md: 3 }}>
          <Image
            src="/ai-icon.png"
            alt="AI Icon"
            boxSize={{ base: '24px', md: '29px' }}
            borderRadius="full"
          />
          <Heading
            size={{ base: 'sm', md: 'md' }}
            color={useColorModeValue('gray.700', 'white')}
          >
            近大高専チャット
          </Heading>
          <Tag
            size="sm"
            bg={useColorModeValue(statusConfig.bg, statusConfig.darkBg)}
            color={useColorModeValue(statusConfig.color, statusConfig.darkColor)}
            borderRadius="full"
            display={{ base: 'none', sm: 'flex' }}
          >
            <Box
              w={2}
              h={2}
              borderRadius="full"
              bg="currentColor"
              mr={2}
            />
            <Text display={{ base: 'none', md: 'block' }}>{statusText[apiStatus]}</Text>
          </Tag>
        </HStack>

        <HStack spacing={{ base: 1, md: 2 }}>
          <HStack
            bg={useColorModeValue('blue.50', 'blue.900')}
            px={3}
            py={1}
            borderRadius="full"
            display={{ base: 'none', sm: 'flex' }}
          >
            <Image
              src={user.photoURL || 'https://via.placeholder.com/32'}
              alt="User"
              boxSize="32px"
              borderRadius="full"
            />
            <Text
              fontSize="sm"
              fontWeight="500"
              display={{ base: 'none', md: 'block' }}
              maxW="120px"
              isTruncated
            >
              {user.displayName || 'ユーザー'}
            </Text>
          </HStack>

          <IconButton
            aria-label="検索履歴"
            icon={<FiClock />}
            variant="ghost"
            colorScheme="blue"
            size={{ base: 'sm', md: 'md' }}
            onClick={onToggleHistory}
          />
          <IconButton
            aria-label="会話をクリア"
            icon={<FiTrash2 />}
            variant="ghost"
            colorScheme="blue"
            size={{ base: 'sm', md: 'md' }}
            onClick={onClearChat}
          />
          <IconButton
            aria-label="ダークモード切替"
            icon={colorMode === 'dark' ? <FiSun /> : <FiMoon />}
            variant="ghost"
            colorScheme="blue"
            size={{ base: 'sm', md: 'md' }}
            onClick={toggleColorMode}
          />
          <IconButton
            aria-label="ログアウト"
            icon={<FiLogOut />}
            variant="ghost"
            colorScheme="blue"
            size={{ base: 'sm', md: 'md' }}
            onClick={onLogout}
          />
        </HStack>
      </Flex>
    </Box>
  );
}

import {
  Box,
  Button,
  Drawer,
  DrawerBody,
  DrawerCloseButton,
  DrawerContent,
  DrawerFooter,
  DrawerHeader,
  DrawerOverlay,
  Flex,
  Icon,
  Text,
  useColorModeValue,
  VStack,
} from '@chakra-ui/react';
import { FiClock, FiSearch, FiTrash2 } from 'react-icons/fi';
import { SearchHistoryItem } from '../types';
import { getTimeAgo } from '../utils/markdown';

interface SearchHistoryPanelProps {
  isOpen: boolean;
  onClose: () => void;
  history: SearchHistoryItem[];
  onSelectQuery: (query: string) => void;
  onClear: () => void;
}

export function SearchHistoryPanel({
  isOpen,
  onClose,
  history,
  onSelectQuery,
  onClear,
}: SearchHistoryPanelProps) {
  const bgColor = useColorModeValue('white', 'gray.800');
  const hoverBg = useColorModeValue('blue.50', 'blue.900');
  const borderColor = useColorModeValue('gray.100', 'gray.700');

  const handleSelect = (query: string) => {
    onSelectQuery(query);
    onClose();
  };

  return (
    <Drawer isOpen={isOpen} onClose={onClose} placement="right" size="sm">
      <DrawerOverlay />
      <DrawerContent bg={bgColor}>
        <DrawerCloseButton />
        <DrawerHeader borderBottomWidth="1px" borderColor={borderColor}>
          <Flex align="center" gap={2}>
            <Icon as={FiClock} color="blue.400" />
            <Text>検索履歴</Text>
          </Flex>
        </DrawerHeader>

        <DrawerBody p={4}>
          {history.length === 0 ? (
            <Text color="gray.500" textAlign="center" py={10}>
              検索履歴がありません
            </Text>
          ) : (
            <VStack spacing={2} align="stretch">
              {history.map((item) => (
                <Box
                  key={item.id}
                  p={3}
                  borderRadius="lg"
                  bg={useColorModeValue('blue.50', 'whiteAlpha.50')}
                  cursor="pointer"
                  transition="all 0.2s"
                  _hover={{
                    bg: hoverBg,
                    borderColor: 'blue.200',
                  }}
                  onClick={() => handleSelect(item.query)}
                  border="1px solid transparent"
                >
                  <Flex align="center" gap={3}>
                    <Icon as={FiSearch} color="blue.400" flexShrink={0} />
                    <Box flex={1} overflow="hidden">
                      <Text
                        fontSize="sm"
                        fontWeight="500"
                        isTruncated
                      >
                        {item.query}
                      </Text>
                      <Text fontSize="xs" color="gray.500">
                        {getTimeAgo(item.timestamp)}
                      </Text>
                    </Box>
                  </Flex>
                </Box>
              ))}
            </VStack>
          )}
        </DrawerBody>

        {history.length > 0 && (
          <DrawerFooter borderTopWidth="1px" borderColor={borderColor}>
            <Button
              leftIcon={<FiTrash2 />}
              colorScheme="red"
              variant="outline"
              w="100%"
              onClick={onClear}
            >
              履歴をクリア
            </Button>
          </DrawerFooter>
        )}
      </DrawerContent>
    </Drawer>
  );
}

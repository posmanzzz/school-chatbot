import { useState, useRef, KeyboardEvent } from 'react';
import {
  Box,
  Checkbox,
  Flex,
  HStack,
  IconButton,
  Textarea,
  useColorModeValue,
} from '@chakra-ui/react';
import { FiSend, FiGlobe } from 'react-icons/fi';

interface ChatInputProps {
  onSend: (message: string, webSearchEnabled: boolean) => Promise<void>;
  isLoading: boolean;
}

export function ChatInput({ onSend, isLoading }: ChatInputProps) {
  const [message, setMessage] = useState('');
  const [webSearchEnabled, setWebSearchEnabled] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const bgColor = useColorModeValue('whiteAlpha.500', 'whiteAlpha.100');
  const inputBg = useColorModeValue('white', 'gray.700');
  const inputBorder = useColorModeValue('blue.200', 'blue.600');

  const handleSubmit = async () => {
    if (!message.trim() || isLoading) return;
    const currentMessage = message;
    setMessage('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
    await onSend(currentMessage, webSearchEnabled);
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleInput = () => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 120)}px`;
    }
  };

  return (
    <Box
      p={4}
      bg={bgColor}
      borderTop="1px solid"
      borderColor={useColorModeValue('blackAlpha.50', 'whiteAlpha.50')}
    >
      <HStack mb={3}>
        <Checkbox
          isChecked={webSearchEnabled}
          onChange={(e) => setWebSearchEnabled(e.target.checked)}
          colorScheme="blue"
          size="sm"
        >
          <HStack spacing={2}>
            <FiGlobe />
            <span>Web検索</span>
          </HStack>
        </Checkbox>
      </HStack>

      <Flex gap={3}>
        <Textarea
          ref={textareaRef}
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          onInput={handleInput}
          placeholder="メッセージを入力..."
          resize="none"
          rows={1}
          minH="50px"
          maxH="120px"
          bg={inputBg}
          border="2px solid"
          borderColor={inputBorder}
          borderRadius="xl"
          _focus={{
            borderColor: 'blue.400',
            boxShadow: '0 0 0 3px rgba(66, 153, 225, 0.1)',
          }}
          _placeholder={{ color: 'gray.400' }}
          fontSize={{ base: '16px', md: 'md' }}
        />
        <IconButton
          aria-label="送信"
          icon={<FiSend />}
          colorScheme="blue"
          size="lg"
          borderRadius="md"
          isLoading={isLoading}
          onClick={handleSubmit}
          isDisabled={!message.trim()}
        />
      </Flex>
    </Box>
  );
}

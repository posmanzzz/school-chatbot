import { useEffect, useRef } from 'react';
import { Box, Icon, Text, useColorModeValue, VStack } from '@chakra-ui/react';
import { FiMessageCircle } from 'react-icons/fi';
import { ChatMessage as ChatMessageType } from '../types';
import { ChatMessage } from './ChatMessage';
import { QuickQuestions } from './QuickQuestions';
import { TypingIndicator } from './TypingIndicator';

interface ChatBoxProps {
  messages: ChatMessageType[];
  isLoading: boolean;
  onQuickQuestion: (question: string) => void;
  userPhotoURL?: string | null;
}

export function ChatBox({ messages, isLoading, onQuickQuestion, userPhotoURL }: ChatBoxProps) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const bgColor = useColorModeValue('gray.50', 'gray.900');

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTo({
        top: scrollRef.current.scrollHeight,
        behavior: 'smooth',
      });
    }
  }, [messages, isLoading]);

  const showWelcome = messages.length === 0;

  return (
    <Box
      ref={scrollRef}
      flex={1}
      overflowY="auto"
      p={6}
      bg={bgColor}
      css={{
        '&::-webkit-scrollbar': {
          width: '8px',
        },
        '&::-webkit-scrollbar-track': {
          background: 'transparent',
        },
        '&::-webkit-scrollbar-thumb': {
          background: 'rgba(0, 123, 255, 0.3)',
          borderRadius: '4px',
        },
        '&::-webkit-scrollbar-thumb:hover': {
          background: 'rgba(0, 123, 255, 0.5)',
        },
      }}
    >
      <VStack spacing={4} align="stretch" minH="100%">
        {showWelcome && (
          <VStack spacing={4} py={10} textAlign="center">
            <Icon
              as={FiMessageCircle}
              boxSize={12}
              color="blue.400"
              opacity={0.7}
            />
            <Text color="gray.500" fontSize="lg">
              こんにちは！近大高専について何でも聞いてください。
            </Text>
            <QuickQuestions onQuestionClick={onQuickQuestion} />
          </VStack>
        )}

        {messages.map((message, index) => (
          <ChatMessage key={index} message={message} userPhotoURL={userPhotoURL} />
        ))}

        {isLoading && <TypingIndicator />}
      </VStack>
    </Box>
  );
}

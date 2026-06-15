import { Box, useColorModeValue } from '@chakra-ui/react';
import { ChatMessage } from '../types';
import { ChatBox } from './ChatBox';
import { ChatInput } from './ChatInput';

interface ChatContainerProps {
  messages: ChatMessage[];
  isLoading: boolean;
  onSendMessage: (message: string, webSearchEnabled: boolean) => Promise<void>;
  onQuickQuestion: (question: string) => void;
  userPhotoURL?: string | null;
}

export function ChatContainer({
  messages,
  isLoading,
  onSendMessage,
  onQuickQuestion,
  userPhotoURL,
}: ChatContainerProps) {
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');

  return (
    <Box
      flex={1}
      maxW="700px"
      w="100%"
      h={{ base: 'calc(100vh - 130px)', lg: 'calc(100vh - 140px)' }}
      bg={bgColor}
      borderRadius="lg"
      border="1px solid"
      borderColor={borderColor}
      boxShadow="sm"
      display="flex"
      flexDirection="column"
      overflow="hidden"
    >
      <ChatBox
        messages={messages}
        isLoading={isLoading}
        onQuickQuestion={onQuickQuestion}
        userPhotoURL={userPhotoURL}
      />
      <ChatInput onSend={onSendMessage} isLoading={isLoading} />
    </Box>
  );
}

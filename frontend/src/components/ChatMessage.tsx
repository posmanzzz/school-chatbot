import { useState } from 'react';
import {
  Box,
  Flex,
  IconButton,
  Image,
  Link,
  Text,
  useColorModeValue,
  useToast,
  VStack,
} from '@chakra-ui/react';
import { FiCopy, FiCheck, FiExternalLink } from 'react-icons/fi';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeSanitize from 'rehype-sanitize';
import { ChatMessage as ChatMessageType } from '../types';

interface ChatMessageProps {
  message: ChatMessageType;
  userPhotoURL?: string | null;
}

export function ChatMessage({ message, userPhotoURL }: ChatMessageProps) {
  const [copied, setCopied] = useState(false);
  const toast = useToast();
  const isUser = message.sender === 'user';

  const userBg = useColorModeValue('blue.500', 'blue.600');
  const aiBg = useColorModeValue('white', 'gray.700');
  const aiTextColor = useColorModeValue('gray.800', 'gray.100');

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(message.content);
      setCopied(true);
      toast({
        title: 'コピーしました',
        status: 'success',
        duration: 2000,
        isClosable: true,
        position: 'bottom',
      });
      setTimeout(() => setCopied(false), 2000);
    } catch {
      toast({
        title: 'コピーに失敗しました',
        status: 'error',
        duration: 2000,
        isClosable: true,
      });
    }
  };

  return (
    <Box
      alignSelf={isUser ? 'flex-end' : 'flex-start'}
      maxW="80%"
    >
      <Flex
        direction={isUser ? 'row-reverse' : 'row'}
        align="flex-start"
        gap={3}
      >
        <Image
          src={isUser ? (userPhotoURL || '/default-user.png') : '/ai-icon.png'}
          alt={isUser ? 'User' : 'AI'}
          boxSize={8}
          borderRadius="full"
          flexShrink={0}
          bg={isUser ? 'gray.200' : 'blue.500'}
        />

        <Box
          bg={isUser ? userBg : aiBg}
          color={isUser ? 'white' : aiTextColor}
          px={4}
          py={3}
          borderRadius="xl"
          borderBottomRightRadius={isUser ? 'sm' : 'xl'}
          borderBottomLeftRadius={isUser ? 'xl' : 'sm'}
          boxShadow={isUser ? 'none' : '0 2px 10px rgba(0, 0, 0, 0.05)'}
          position="relative"
          _hover={{
            '& .copy-btn': {
              opacity: 1,
            },
          }}
        >
          {!isUser && (
            <IconButton
              aria-label="コピー"
              icon={copied ? <FiCheck /> : <FiCopy />}
              size="xs"
              variant="ghost"
              position="absolute"
              top={2}
              right={2}
              opacity={0}
              className="copy-btn"
              onClick={handleCopy}
              color={copied ? 'green.500' : 'gray.500'}
              transition="opacity 0.2s"
            />
          )}

          {isUser ? (
            <Text whiteSpace="pre-wrap">{message.content}</Text>
          ) : (
            <Box
              className="markdown-body"
              sx={{
                'p': { mb: 3, _last: { mb: 0 } },
                'h1, h2, h3': { mt: 4, mb: 2, fontWeight: 'bold' },
                'h1': { fontSize: '1.4em' },
                'h2': { fontSize: '1.25em' },
                'h3': { fontSize: '1.1em' },
                'ul, ol': { pl: 6, my: 2 },
                'li': { my: 1 },
                'code': {
                  bg: useColorModeValue('gray.100', 'gray.600'),
                  px: 2,
                  py: 0.5,
                  borderRadius: 'md',
                  fontSize: '0.9em',
                },
                'pre': {
                  bg: useColorModeValue('gray.900', 'gray.900'),
                  color: 'gray.100',
                  p: 4,
                  borderRadius: 'lg',
                  overflowX: 'auto',
                  my: 3,
                },
                'pre code': {
                  bg: 'transparent',
                  p: 0,
                },
                'blockquote': {
                  borderLeft: '4px solid',
                  borderColor: 'blue.400',
                  pl: 4,
                  py: 2,
                  my: 3,
                  bg: useColorModeValue('blue.50', 'blue.900'),
                },
                'a': {
                  color: 'blue.400',
                  _hover: { textDecoration: 'underline' },
                },
                'table': {
                  width: '100%',
                  my: 3,
                  borderCollapse: 'collapse',
                  display: 'block',
                  overflowX: 'auto',
                },
                'thead': {
                  bg: useColorModeValue('gray.50', 'gray.700'),
                },
                'th, td': {
                  border: '1px solid',
                  borderColor: useColorModeValue('gray.300', 'gray.600'),
                  p: 2,
                  textAlign: 'left',
                  minWidth: '100px',
                },
                'th': {
                  bg: useColorModeValue('gray.100', 'gray.700'),
                  fontWeight: 'bold',
                },
                'tr:nth-of-type(even)': {
                  bg: useColorModeValue('gray.50', 'gray.800'),
                },
              }}
            >
              <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                rehypePlugins={[rehypeSanitize]}
              >
                {message.content}
              </ReactMarkdown>
            </Box>
          )}

          {!isUser && message.sources && message.sources.length > 0 && (
            <VStack
              align="stretch"
              mt={4}
              pt={4}
              borderTop="1px solid"
              borderColor={useColorModeValue('gray.200', 'gray.600')}
              spacing={2}
            >
              <Flex align="center" gap={2} color="gray.500" fontSize="sm">
                <FiExternalLink />
                <Text fontWeight="600">参照元</Text>
              </Flex>
              {message.sources.map((source, index) => (
                <Link
                  key={index}
                  href={source.url}
                  isExternal
                  color="blue.400"
                  fontSize="sm"
                  _hover={{ textDecoration: 'underline' }}
                >
                  {source.title || source.url}
                </Link>
              ))}
            </VStack>
          )}
        </Box>
      </Flex>
    </Box>
  );
}

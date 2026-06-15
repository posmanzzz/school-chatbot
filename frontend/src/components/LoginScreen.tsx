import {
  Box,
  Button,
  Card,
  CardBody,
  Heading,
  Image,
  Text,
  VStack,
  HStack,
  useColorModeValue,
} from '@chakra-ui/react';

interface LoginScreenProps {
  onLogin: () => Promise<void>;
  isLoading: boolean;
}

export function LoginScreen({ onLogin, isLoading }: LoginScreenProps) {
  const bgColor = useColorModeValue('white', 'gray.800');
  const textColor = useColorModeValue('gray.700', 'gray.100');
  const subTextColor = useColorModeValue('gray.500', 'gray.400');

  return (
    <Box
      minH="100vh"
      display="flex"
      alignItems="center"
      justifyContent="center"
      p={5}
      bg={useColorModeValue('gray.50', 'gray.900')}
    >
      <Card
        maxW="400px"
        w="100%"
        bg={bgColor}
        borderRadius="lg"
        boxShadow="md"
      >
        <CardBody p={{ base: 8, md: 12 }}>
          <VStack spacing={6}>
            <Image
              src="/ai-icon.png"
              alt="AI Icon"
              boxSize={{ base: '56px', md: '64px' }}
              borderRadius="xl"
            />
            <VStack spacing={2}>
              <Heading size="lg" color={textColor}>
                近大高専チャット
              </Heading>
              <Text color={subTextColor} textAlign="center" fontSize="sm">
                学校の情報について何でも聞けるAIアシスタント
              </Text>
            </VStack>

            <Button
              w="100%"
              size="lg"
              variant="outline"
              borderColor={useColorModeValue('gray.300', 'gray.600')}
              _hover={{ bg: useColorModeValue('gray.50', 'gray.700') }}
              onClick={onLogin}
              isLoading={isLoading}
              loadingText="ログイン中..."
            >
              <HStack spacing={3}>
                <Image
                  src="https://www.gstatic.com/firebasejs/ui/2.0.0/images/auth/google.svg"
                  alt="Google"
                  boxSize="20px"
                />
                <Text>Googleでログイン</Text>
              </HStack>
            </Button>

            <Text fontSize="xs" color={subTextColor}>
              ログインすると会話履歴が保存されます
            </Text>
          </VStack>
        </CardBody>
      </Card>
    </Box>
  );
}

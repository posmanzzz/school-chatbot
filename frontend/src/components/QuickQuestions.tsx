import { Button, Text, VStack, Wrap, WrapItem, useColorModeValue } from '@chakra-ui/react';
import {
  FiAward,
  FiBook,
  FiCalendar,
  FiHome,
  FiTarget,
  FiUsers,
} from 'react-icons/fi';

interface QuickQuestionsProps {
  onQuestionClick: (question: string) => void;
}

const QUESTIONS = [
  { text: '入学試験', question: '入学試験について教えてください', icon: FiAward },
  { text: '学科紹介', question: '学科の特徴を教えてください', icon: FiBook },
  { text: '行事予定', question: '年間行事予定を教えてください', icon: FiCalendar },
  { text: '資格取得', question: '取得できる資格について教えてください', icon: FiTarget },
  { text: '部活動', question: '部活動について教えてください', icon: FiUsers },
  { text: '学生寮', question: '寮について教えてください', icon: FiHome },
];

export function QuickQuestions({ onQuestionClick }: QuickQuestionsProps) {
  const buttonBg = useColorModeValue('blue.50', 'blue.900');
  const buttonColor = useColorModeValue('blue.600', 'blue.200');
  const buttonBorder = useColorModeValue('blue.200', 'blue.700');

  return (
    <VStack spacing={4} py={4}>
      <Text fontSize="sm" color="gray.500" fontWeight="500">
        よくある質問:
      </Text>
      <Wrap spacing={2} justify="center">
        {QUESTIONS.map((q, index) => (
          <WrapItem key={index}>
            <Button
              leftIcon={<q.icon />}
              size="sm"
              variant="outline"
              bg={buttonBg}
              color={buttonColor}
              borderColor={buttonBorder}
              borderRadius="md"
              fontWeight="500"
              onClick={() => onQuestionClick(q.question)}
              _hover={{
                bg: useColorModeValue('blue.100', 'blue.800'),
              }}
            >
              {q.text}
            </Button>
          </WrapItem>
        ))}
      </Wrap>
    </VStack>
  );
}

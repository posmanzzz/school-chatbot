import {
  Box,
  Heading,
  HStack,
  Icon,
  Link,
  useColorModeValue,
  VStack,
} from '@chakra-ui/react';
import { FiAward, FiCalendar, FiLink } from 'react-icons/fi';

const LINKS = [
  {
    title: '令和7年後期行事予定表',
    url: 'https://www.ktc.ac.jp/img/students/schedule/2025/2025_yotei_kouki.pdf',
    icon: FiCalendar,
  },
  {
    title: '令和8年前期行事予定表',
    url: 'https://www.ktc.ac.jp/img/students/schedule/2026/2026_yotei_zenki.pdf',
    icon: FiCalendar,
  },
  {
    title: '資格支援表',
    url: 'https://www.ktc.ac.jp/img/students/shikaku/shikaku_syutoku_list_2025.pdf',
    icon: FiAward,
  },
];

export function SideLinks() {
  const bgColor = useColorModeValue('white', 'gray.800');
  const hoverBg = useColorModeValue('gray.50', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.700');

  return (
    <Box w="220px" flexShrink={0} display={{ base: 'none', lg: 'block' }}>
      <Box
        bg={bgColor}
        borderRadius="md"
        p={4}
        mb={4}
        border="1px solid"
        borderColor={borderColor}
      >
        <HStack color="gray.500" mb={3}>
          <Icon as={FiLink} />
          <Heading size="sm">クイックリンク</Heading>
        </HStack>
      </Box>

      <VStack spacing={3} align="stretch">
        {LINKS.map((link, index) => (
          <Link
            key={index}
            href={link.url}
            isExternal
            bg={bgColor}
            borderRadius="md"
            p={4}
            border="1px solid"
            borderColor={borderColor}
            _hover={{
              bg: hoverBg,
              textDecoration: 'none',
            }}
          >
            <HStack spacing={3}>
              <Icon as={link.icon} color="blue.400" />
              <Box fontSize="sm" fontWeight="500">
                {link.title}
              </Box>
            </HStack>
          </Link>
        ))}
      </VStack>
    </Box>
  );
}

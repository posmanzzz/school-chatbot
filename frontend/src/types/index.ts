import { User } from 'firebase/auth';

export interface ChatMessage {
  content: string;
  sender: 'user' | 'ai';
  sources?: Source[];
  timestamp?: string;
}

export interface Source {
  url: string;
  title?: string;
}

export interface SearchHistoryItem {
  id: string;
  query: string;
  timestamp: Date;
}

export interface ScheduleAlert {
  type: 'exam' | 'holiday' | 'closed' | 'event';
  icon: string;
  color: string;
  title: string;
  message: string;
}

export interface ExamPeriod {
  start: string;
  end: string;
  name: string;
}

export interface HolidayPeriod {
  start: string;
  end: string;
  name: string;
}

export interface ClosedDay {
  date: string;
  name: string;
}

export interface SchoolEvent {
  date: string;
  name: string;
}

export interface ScheduleData {
  exams: ExamPeriod[];
  holidays: HolidayPeriod[];
  closedDays: ClosedDay[];
  events: SchoolEvent[];
}

export interface ApiResponse {
  response: string;
  sources: Source[];
}

export interface AuthContextType {
  user: User | null;
  loading: boolean;
  signInWithGoogle: () => Promise<void>;
  signOut: () => Promise<void>;
}

export interface ChatContextType {
  messages: ChatMessage[];
  isLoading: boolean;
  sendMessage: (message: string, webSearchEnabled: boolean) => Promise<void>;
  clearMessages: () => Promise<void>;
}

export type ApiStatus = 'online' | 'offline' | 'connecting';

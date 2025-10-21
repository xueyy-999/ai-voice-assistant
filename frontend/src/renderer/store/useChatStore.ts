/**
 * 对话状态管理
 */
import { create } from 'zustand';

interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: number;
  steps?: any[];
}

interface ChatState {
  messages: Message[];
  sessionId: string | null;
  isThinking: boolean;
  currentSteps: any[];
  currentStepIndex: number;

  addMessage: (message: Omit<Message, 'id' | 'timestamp'>) => void;
  setThinking: (thinking: boolean) => void;
  clearMessages: () => void;
  setSessionId: (id: string) => void;
  setCurrentSteps: (steps: any[]) => void;
  setCurrentStepIndex: (index: number) => void;
  clearSteps: () => void;
}

export const useChatStore = create<ChatState>((set) => ({
  messages: [],
  sessionId: null,
  isThinking: false,
  currentSteps: [],
  currentStepIndex: -1,

  addMessage: (message) =>
    set((state) => ({
      messages: [
        ...state.messages,
        {
          ...message,
          id: `msg-${Date.now()}-${Math.random()}`,
          timestamp: Date.now(),
        },
      ],
    })),

  setThinking: (thinking) => set({ isThinking: thinking }),

  clearMessages: () => set({ messages: [] }),

  setSessionId: (id) => set({ sessionId: id }),

  setCurrentSteps: (steps) => set({ currentSteps: steps }),

  setCurrentStepIndex: (index) => set({ currentStepIndex: index }),

  clearSteps: () => set({ currentSteps: [], currentStepIndex: -1 }),
}));

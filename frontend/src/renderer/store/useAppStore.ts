/**
 * 应用全局状态
 */
import { create } from 'zustand';

interface AppState {
  // 连接状态
  isConnected: boolean;
  setConnected: (connected: boolean) => void;

  // 语音状态
  isRecording: boolean;
  setRecording: (recording: boolean) => void;

  // 音量
  volume: number;
  setVolume: (volume: number) => void;

  // 系统信息
  systemInfo: any;
  setSystemInfo: (info: any) => void;

  // 加载状态
  isLoading: boolean;
  setLoading: (loading: boolean) => void;
}

export const useAppStore = create<AppState>((set) => ({
  isConnected: false,
  setConnected: (connected) => set({ isConnected: connected }),

  isRecording: false,
  setRecording: (recording) => set({ isRecording: recording }),

  volume: 0,
  setVolume: (volume) => set({ volume }),

  systemInfo: null,
  setSystemInfo: (info) => set({ systemInfo: info }),

  isLoading: false,
  setLoading: (loading) => set({ isLoading: loading }),
}));


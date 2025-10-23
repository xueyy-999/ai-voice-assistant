/**
 * HTTP API客户端
 */
import axios from 'axios';

// 允许从环境变量或全局配置覆盖
const API_BASE_URL = (globalThis as any).__API_BASE_URL__
  || (import.meta as any).env?.VITE_API_BASE_URL
  || 'http://localhost:8000/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

export const api = {
  // 健康检查
  health: () => apiClient.get('/system/health'),

  // 语音接口
  voice: {
    recognize: (audioBlob: Blob) => {
      const formData = new FormData();
      formData.append('audio', audioBlob, 'audio.wav');
      return apiClient.post('/voice/recognize', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
    },
    synthesize: (text: string, voice?: string) =>
      apiClient.post('/voice/synthesize', { text, voice }),
    getVoices: () => apiClient.get('/voice/voices'),
  },

  // 对话接口
  chat: {
    send: (message: string, sessionId?: string) =>
      apiClient.post('/chat/send', { message, session_id: sessionId }),
    getHistory: (sessionId: string, limit = 50) =>
      apiClient.get('/chat/history', { params: { session_id: sessionId, limit } }),
  },

  // 任务接口
  task: {
    execute: (command: string, params?: any) =>
      apiClient.post('/task/execute', { command, params }),
    getStatus: (taskId: string) => apiClient.get(`/task/status/${taskId}`),
    cancel: (taskId: string) => apiClient.post(`/task/cancel/${taskId}`),
  },

  // 系统接口
  system: {
    getInfo: () => apiClient.get('/system/info'),
    getApps: () => apiClient.get('/system/apps'),
    updateConfig: (key: string, value: any) =>
      apiClient.post('/system/config', { key, value }),
  },
};


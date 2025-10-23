/**
 * WebSocket客户端
 */

type MessageHandler = (message: any) => void;

export class WebSocketClient {
  private ws: WebSocket | null = null;
  private url: string;
  private handlers: Map<string, MessageHandler[]> = new Map();
  private reconnectAttempts = 0;
  private maxReconnectAttempts = Number.MAX_SAFE_INTEGER; // 无限重连
  private reconnectDelay = 2000;

  constructor(url?: string) {
    const protocol = location.protocol === 'https:' ? 'wss' : 'ws';
    const host = location.hostname || '127.0.0.1';
    const defaultWs = `${protocol}://${host}:8000/api/chat/ws`;
    const configured = (globalThis as any).__WS_URL__
      || (import.meta as any).env?.VITE_WS_URL
      || defaultWs;
    this.url = url || configured;
  }

  public getUrl(): string {
    return this.url;
  }

  private emit(type: string, payload?: any) {
    const handlers = this.handlers.get(type) || [];
    handlers.forEach((handler) => handler(payload));
  }

  connect(): Promise<void> {
    return new Promise((resolve) => {
      try {
        this.ws = new WebSocket(this.url);

        this.ws.onopen = () => {
          console.log('✅ WebSocket connected');
          this.reconnectAttempts = 0;
          this.startHeartbeat();
          this.emit('ws_open');
          resolve();
        };

        this.ws.onmessage = (event) => {
          try {
            const message = JSON.parse(event.data);
            this.handleMessage(message);
          } catch (e) {
            console.error('Failed to parse message:', e);
          }
        };

        this.ws.onerror = (error) => {
          console.error('❌ WebSocket error:', error);
          // 出错也尝试重连，不reject以便后续能够成功后resolve
          this.attemptReconnect();
        };

        this.ws.onclose = () => {
          console.log('👋 WebSocket disconnected');
          this.emit('ws_close');
          this.attemptReconnect();
        };
      } catch (error) {
        console.error('❌ WebSocket connect failed:', error);
        this.attemptReconnect();
      }
    });
  }

  private handleMessage(message: any) {
    const type = message.type;
    const handlers = this.handlers.get(type) || [];
    handlers.forEach(handler => handler(message));

    // 触发通用处理器
    const allHandlers = this.handlers.get('*') || [];
    allHandlers.forEach(handler => handler(message));
  }

  on(type: string, handler: MessageHandler) {
    if (!this.handlers.has(type)) {
      this.handlers.set(type, []);
    }
    this.handlers.get(type)!.push(handler);
  }

  off(type: string, handler: MessageHandler) {
    const handlers = this.handlers.get(type);
    if (handlers) {
      const index = handlers.indexOf(handler);
      if (index > -1) {
        handlers.splice(index, 1);
      }
    }
  }

  send(message: any): boolean {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      // 如果message是对象，直接发送；如果是字符串格式的type和data，转换
      const payload = typeof message === 'object' && message.type
        ? message
        : { type: 'message', data: message, timestamp: Date.now() };
      this.ws.send(JSON.stringify(payload));
      return true;
    } else {
      console.warn('WebSocket is not connected');
      return false;
    }
  }

  private heartbeatInterval: any = null;

  private startHeartbeat() {
    this.heartbeatInterval = setInterval(() => {
      this.send({ type: 'ping', data: {} });
    }, 15000); // 每15秒心跳
  }

  private attemptReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) return;
    this.reconnectAttempts++;
    console.log(`Attempting to reconnect (${this.reconnectAttempts})...`);
    setTimeout(() => {
      this.connect().catch(() => {
        // 忽略异常，继续由内部逻辑重连
      });
    }, this.reconnectDelay);
  }

  disconnect() {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
    }
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN;
  }
}

// 全局实例
export const wsClient = new WebSocketClient();


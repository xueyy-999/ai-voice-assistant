/**
 * 音频采集模块 - Web Audio API
 */

export class AudioCapture {
  private mediaStream: MediaStream | null = null;
  private audioContext: AudioContext | null = null;
  private mediaRecorder: MediaRecorder | null = null;
  private audioChunks: Blob[] = [];
  private isRecording = false;

  // 回调函数
  public onDataAvailable?: (blob: Blob) => void;
  public onError?: (error: Error) => void;
  public onVolumeChange?: (volume: number) => void;

  async initialize(): Promise<void> {
    try {
      // 请求麦克风权限
      this.mediaStream = await navigator.mediaDevices.getUserMedia({
        audio: {
          channelCount: 1,
          sampleRate: 16000,
          echoCancellation: true,
          noiseSuppression: true,
        },
      });

      // 创建音频上下文
      this.audioContext = new AudioContext({ sampleRate: 16000 });

      // 创建MediaRecorder
      this.mediaRecorder = new MediaRecorder(this.mediaStream, {
        mimeType: 'audio/webm',
      });

      this.mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          this.audioChunks.push(event.data);
        }
      };

      this.mediaRecorder.onstop = () => {
        const audioBlob = new Blob(this.audioChunks, { type: 'audio/wav' });
        this.audioChunks = [];
        if (this.onDataAvailable) {
          this.onDataAvailable(audioBlob);
        }
      };

      console.log('✅ Audio capture initialized');
    } catch (error) {
      console.error('❌ Failed to initialize audio capture:', error);
      if (this.onError) {
        this.onError(error as Error);
      }
      throw error;
    }
  }

  startRecording(): void {
    if (!this.mediaRecorder) {
      console.error('MediaRecorder not initialized');
      return;
    }

    if (this.isRecording) {
      console.warn('Already recording');
      return;
    }

    this.audioChunks = [];
    this.mediaRecorder.start();
    this.isRecording = true;
    this.startVolumeMonitoring();

    console.log('🎤 Recording started');
  }

  stopRecording(): void {
    if (!this.mediaRecorder || !this.isRecording) {
      return;
    }

    this.mediaRecorder.stop();
    this.isRecording = false;
    this.stopVolumeMonitoring();

    console.log('⏹️ Recording stopped');
  }

  private volumeMonitorInterval: any = null;
  private analyser: AnalyserNode | null = null;

  private startVolumeMonitoring(): void {
    if (!this.audioContext || !this.mediaStream) return;

    const source = this.audioContext.createMediaStreamSource(this.mediaStream);
    this.analyser = this.audioContext.createAnalyser();
    this.analyser.fftSize = 256;
    source.connect(this.analyser);

    const bufferLength = this.analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);

    this.volumeMonitorInterval = setInterval(() => {
      if (!this.analyser) return;

      this.analyser.getByteFrequencyData(dataArray);
      const volume = dataArray.reduce((a, b) => a + b, 0) / bufferLength / 255;

      if (this.onVolumeChange) {
        this.onVolumeChange(volume);
      }
    }, 100);
  }

  private stopVolumeMonitoring(): void {
    if (this.volumeMonitorInterval) {
      clearInterval(this.volumeMonitorInterval);
      this.volumeMonitorInterval = null;
    }
  }

  getRecordingState(): boolean {
    return this.isRecording;
  }

  destroy(): void {
    this.stopRecording();
    
    if (this.mediaStream) {
      this.mediaStream.getTracks().forEach(track => track.stop());
      this.mediaStream = null;
    }

    if (this.audioContext) {
      this.audioContext.close();
      this.audioContext = null;
    }

    console.log('🗑️ Audio capture destroyed');
  }
}


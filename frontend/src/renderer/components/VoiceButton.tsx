/**
 * 语音输入按钮组件
 */
import React, { useState, useEffect } from 'react';
import { useAppStore } from '../store/useAppStore';
import { useChatStore } from '../store/useChatStore';
import { AudioCapture } from '../services/audioCapture';
import { api } from '../services/api';

let audioCapture: AudioCapture | null = null;

export const VoiceButton: React.FC = () => {
  const [isInitialized, setIsInitialized] = useState(false);
  const { isRecording, setRecording, volume, setVolume } = useAppStore();
  const { addMessage, setThinking } = useChatStore();

  useEffect(() => {
    // 初始化音频采集
    initAudio();

    return () => {
      if (audioCapture) {
        audioCapture.destroy();
      }
    };
  }, []);

  const initAudio = async () => {
    try {
      audioCapture = new AudioCapture();

      audioCapture.onVolumeChange = (vol) => {
        setVolume(vol);
      };

      audioCapture.onDataAvailable = async (blob) => {
        console.log('📦 Audio recorded:', blob.size, 'bytes');

        try {
          setThinking(true);

          // 发送到后端识别
          const result = await api.voice.recognize(blob);
          console.log('🎤 Recognition result:', result);

          const recognizedText = result.text;

          // 添加用户消息
          addMessage({
            role: 'user',
            content: recognizedText,
          });

          // 发送到AI处理
          const chatResult = await api.chat.send(recognizedText);
          console.log('💬 Chat result:', chatResult);

          // 添加AI回复
          addMessage({
            role: 'assistant',
            content: chatResult.reply,
            intent: chatResult.intent,
          });

          // 语音播报回复
          if (chatResult.reply) {
            await playTTS(chatResult.reply);
          }
        } catch (error) {
          console.error('❌ Error processing audio:', error);
          addMessage({
            role: 'system',
            content: '抱歉，处理失败了，请重试',
          });
        } finally {
          setThinking(false);
        }
      };

      audioCapture.onError = (error) => {
        console.error('Audio capture error:', error);
        alert('麦克风访问失败，请检查权限设置');
      };

      await audioCapture.initialize();
      setIsInitialized(true);
      console.log('✅ Audio initialized');
    } catch (error) {
      console.error('Failed to init audio:', error);
      alert('无法访问麦克风，请检查浏览器权限');
    }
  };

  const playTTS = async (text: string) => {
    try {
      const result = await api.voice.synthesize(text);
      if (result.audio) {
        // 播放音频
        const audioData = atob(result.audio);
        const audioArray = new Uint8Array(audioData.length);
        for (let i = 0; i < audioData.length; i++) {
          audioArray[i] = audioData.charCodeAt(i);
        }
        const audioBlob = new Blob([audioArray], { type: 'audio/mp3' });
        const audioUrl = URL.createObjectURL(audioBlob);
        const audio = new Audio(audioUrl);
        await audio.play();
      }
    } catch (error) {
      console.error('TTS playback failed:', error);
    }
  };

  const handleMouseDown = () => {
    if (!isInitialized || !audioCapture) return;
    audioCapture.startRecording();
    setRecording(true);
  };

  const handleMouseUp = () => {
    if (!isInitialized || !audioCapture) return;
    audioCapture.stopRecording();
    setRecording(false);
  };

  return (
    <div className="flex flex-col items-center gap-4">
      {/* 音量指示器 */}
      {isRecording && (
        <div className="w-64 h-2 bg-gray-200 rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-blue-400 to-purple-500 transition-all duration-100"
            style={{ width: `${volume * 100}%` }}
          />
        </div>
      )}

      {/* 语音按钮 */}
      <button
        onMouseDown={handleMouseDown}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        disabled={!isInitialized}
        className={`
          w-24 h-24 rounded-full flex items-center justify-center
          transition-all duration-200 shadow-lg
          ${
            isRecording
              ? 'bg-red-500 scale-110 shadow-red-500/50'
              : 'bg-gradient-to-br from-blue-500 to-purple-600 hover:scale-105'
          }
          ${!isInitialized && 'opacity-50 cursor-not-allowed'}
        `}
      >
        <svg
          className="w-12 h-12 text-white"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"
          />
        </svg>
      </button>

      {/* 提示文字 */}
      <p className="text-sm text-gray-600">
        {!isInitialized
          ? '正在初始化...'
          : isRecording
          ? '🎤 正在录音...'
          : '按住说话'}
      </p>
    </div>
  );
};


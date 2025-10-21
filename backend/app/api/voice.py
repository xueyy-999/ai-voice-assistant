"""
语音相关API
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from app.services.voice.stt_service import stt_service
from app.services.voice.tts_service import tts_service
from app.utils.logger import logger

router = APIRouter()


class RecognizeResponse(BaseModel):
    """语音识别响应"""
    text: str
    confidence: float


class SynthesizeRequest(BaseModel):
    """语音合成请求"""
    text: str
    voice: str = "zh-CN-XiaoxiaoNeural"


class SynthesizeResponse(BaseModel):
    """语音合成响应"""
    audio: str
    format: str


@router.post("/recognize", response_model=RecognizeResponse)
async def recognize_voice(audio: UploadFile = File(...)):
    """
    语音识别接口
    
    - 接收音频文件
    - 返回识别的文本和置信度
    """
    try:
        # 读取音频数据
        audio_data = await audio.read()
        
        # 调用STT服务
        result = await stt_service.recognize(audio_data, "wav")
        
        if not result or not result.success:
            raise HTTPException(status_code=400, detail="语音识别失败")
        
        return RecognizeResponse(
            text=result.text,
            confidence=result.confidence
        )
    
    except Exception as e:
        logger.error(f"语音识别API错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/synthesize", response_model=SynthesizeResponse)
async def synthesize_voice(request: SynthesizeRequest):
    """
    语音合成接口
    
    - 接收文本
    - 返回合成的音频（base64编码）
    """
    try:
        # 调用TTS服务
        result = await tts_service.synthesize(request.text, request.voice)
        
        if not result:
            raise HTTPException(status_code=400, detail="语音合成失败")
        
        return SynthesizeResponse(
            audio=result.get("audio", ""),
            format=result.get("format", "mp3")
        )
    
    except Exception as e:
        logger.error(f"语音合成API错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/voices")
async def get_voices():
    """
    获取可用音色列表
    """
    return {
        "voices": tts_service.get_available_voices()
    }

import os
import json
import requests
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "")
MODEL = os.getenv("DEEPSEEK_MODEL", "qwen-turbo")

def norm(u: str) -> str:
    if not u:
        return u
    u = u.strip().replace('，', ',').replace(' ', '').replace(',', '.')
    return u

BASE_URL = norm(BASE_URL)
print("检查模型接口...")
print(f"base_url={BASE_URL} model={MODEL} key={API_KEY[:6]}***")

if not API_KEY or not BASE_URL:
    print("❌ 未读取到 API Key 或 Base URL，请检查 backend/.env")
    raise SystemExit(1)

url = f"{BASE_URL}/chat/completions"
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}
data = {
    "model": MODEL,
    "messages": [{"role": "user", "content": "你好"}],
    "max_tokens": 32,
}

try:
    resp = requests.post(url, headers=headers, json=data, timeout=20)
    print(f"状态码: {resp.status_code}")
    print("响应体:")
    print(resp.text)
except Exception as e:
    print(f"❌ 请求失败: {e}")

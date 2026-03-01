"""动态请求头生成器"""

import base64
import random
import string
import uuid
from typing import Dict

from app.core.logger import logger


_DEFAULT_USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"


def _random_string(length: int, letters_only: bool = True) -> str:
    """生成随机字符串"""
    chars = string.ascii_lowercase if letters_only else string.ascii_lowercase + string.digits
    return ''.join(random.choices(chars, k=length))


def _generate_statsig_id() -> str:
    """生成 x-statsig-id

    随机选择两种格式：
    1. e:TypeError: Cannot read properties of null (reading 'children['xxxxx']')
    2. e:TypeError: Cannot read properties of undefined (reading 'xxxxxxxxxx')
    """
    if random.choice([True, False]):
        rand = _random_string(5, letters_only=False)
        msg = f"e:TypeError: Cannot read properties of null (reading 'children['{rand}']')"
    else:
        rand = _random_string(10)
        msg = f"e:TypeError: Cannot read properties of undefined (reading '{rand}')"

    return base64.b64encode(msg.encode()).decode()


def get_dynamic_headers(pathname: str = "/rest/app-chat/conversations/new") -> Dict[str, str]:
    """获取动态请求头

    Args:
        pathname: 请求路径

    Returns:
        完整的请求头字典
    """
    # 生成动态 statsig-id
    statsig_id = _generate_statsig_id()

    try:
        from app.core.config import get_config
        user_agent = get_config("proxy.user_agent", _DEFAULT_USER_AGENT)
    except Exception:
        user_agent = _DEFAULT_USER_AGENT

    # 构建请求头
    headers = {
        "Accept": "*/*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Connection": "keep-alive",
        "Origin": "https://grok.com",
        "Priority": "u=1, i",
        "User-Agent": user_agent,
        "Sec-Ch-Ua": '"Not(A:Brand";v="99", "Google Chrome";v="136", "Chromium";v="136"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"macOS"',
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Baggage": "sentry-environment=production,sentry-public_key=b311e0f2690c81f25e2c4cf6d4f7ce1c",
        "x-statsig-id": statsig_id,
        "x-xai-request-id": str(uuid.uuid4()),
        "Content-Type": "text/plain;charset=UTF-8" if "upload-file" in pathname else "application/json"
    }

    logger.debug(f"[Headers] 生成动态请求头，statsig-id: {statsig_id[:20]}...")
    return headers

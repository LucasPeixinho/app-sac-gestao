from typing import Optional

from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

from app.core.config import settings

_s = URLSafeTimedSerializer(settings.SESSION_SECRET_KEY)


def create_token(user_id: int, nome: str, papel: str) -> str:
    return _s.dumps({"user_id": user_id, "nome": nome, "papel": papel})


def load_token(token: str) -> Optional[dict]:
    try:
        return _s.loads(token, max_age=28800)  # 8 horas
    except (BadSignature, SignatureExpired):
        return None

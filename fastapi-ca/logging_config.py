import logging
from logging.config import dictConfig

# 로깅 설정
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,  # 기존 로거 비활성화 방지
    "formatters": {
        "default": {
            "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
        },
        "detailed": {
            "format": "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] - %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
        "file": {
            "class": "logging.FileHandler",
            "filename": "app.log",
            "formatter": "detailed",
        },
    },
    "loggers": {
        "uvicorn": {  # uvicorn 로거 설정
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "uvicorn.error": {
            "level": "INFO",
        },
        "uvicorn.access": {
            "level": "INFO",
        },
        "myapp": {  # FastAPI 앱용 커스텀 로거
            "handlers": ["console", "file"],
            "level": "DEBUG",
        },
    },
}

# 설정 적용 함수
def setup_logging():
    dictConfig(LOGGING_CONFIG)

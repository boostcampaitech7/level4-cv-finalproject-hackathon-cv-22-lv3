# logger_config.py
import sys
import os
import logging
from datetime import datetime, timezone, timedelta

# ✅ 로그 파일 저장 경로 설정
os.makedirs("logs", exist_ok=True)  # logs 폴더 생성
kst = timezone(timedelta(hours=9))
timestamp = datetime.now(kst).strftime("%Y%m%d_%H%M%S")
LOG_FILE = f"logs/process_{timestamp}.log"

# ✅ 전역 로거 설정
logger = logging.getLogger("automl_logger")
logger.setLevel(logging.INFO)
logger.propagate = False  # ✅ root logger로 로그 전파 방지 (중복 출력 해결)

# 로그 포맷 지정
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

# 파일 핸들러 추가 (로그 파일 저장, append 모드)
file_handler = logging.FileHandler(LOG_FILE, mode="a", encoding="utf-8")
file_handler.setFormatter(formatter)

# 콘솔 핸들러 추가 (터미널 출력)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)

# ✅ 핸들러 중복 추가 방지 후 등록
if not logger.handlers:
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

# ✅ print()도 로그 파일에 저장되도록 sys.stdout 리디렉션
class TeeLogger:
    def __init__(self, filename):
        self.terminal = sys.stdout
        self.log = open(filename, "a", encoding="utf-8")  # ✅ append 모드

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        self.terminal.flush()
        self.log.flush()

sys.stdout = TeeLogger(LOG_FILE)  # print()도 로그 파일에 저장

# ✅ 다른 파일에서 `from logger_config import logger` 하면 사용 가능

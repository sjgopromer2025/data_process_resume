import os
from dotenv import load_dotenv

load_dotenv()

# 환경 변수 가져오기
processed_path = os.getenv("PROCESSED")
base_path = os.getenv("BASE")
report_path = os.getenv("REPORT")
src_path = os.getenv("PYTHONPATH")

exposed_time = float(os.getenv("EXPOSED_TIME"))
watched_time = float(os.getenv("WATCHED_TIME"))
attention_time = float(os.getenv("ATTENTION_TIME"))

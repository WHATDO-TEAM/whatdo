# Python 3.10 이미지 사용 (필요에 따라 수정 가능)
FROM python:3.10-slim

# 컨테이너 내 작업 디렉토리 설정
WORKDIR /app

# 로컬 코드 복사
COPY . .

# 필요한 패키지 설치
RUN pip install --no-cache-dir -r requirements.txt

# Python 스크립트를 실행
CMD ["sh", "-c", "python preprocessing.py"]
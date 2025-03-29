FROM python:3.10-slim

WORKDIR /app

# התקנת חבילות מערכת נדרשות
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libmagic1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# העתקת קבצי הפרויקט
COPY requirements.txt .
COPY main.py .
COPY transcription/ ./transcription/

# התקנת חבילות Python
RUN pip install --no-cache-dir -r requirements.txt

# חשיפת פורט
EXPOSE 8000

# הפעלת השרת
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"] 
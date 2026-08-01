# Python base image
FROM python:3.10-slim

# FFmpeg install karna
RUN apt-get update && apt-get install -y ffmpeg

# Working directory set karna
WORKDIR /app

# Files copy karna
COPY . /app

# Requirements install karna
RUN pip install -r requirements.txt

# Bot run karna (apni file ka sahi naam likhein agar alag ho toh)
CMD ["python", "insta_bot.py"]

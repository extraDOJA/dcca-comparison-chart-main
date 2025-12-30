# Simple container for running the Streamlit demo on Vercel (Docker deployment) or any container host.

FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy app source
COPY . .

# Streamlit listens on PORT provided by the platform (default 8080)
EXPOSE 8080
CMD ["sh", "-c", "PORT=${PORT:-8080}; streamlit run app.py --server.address 0.0.0.0 --server.port $PORT"]

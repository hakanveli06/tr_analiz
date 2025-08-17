# 1. Adım: Resmi ve hafif bir Python ortamıyla başla
FROM python:3.11-slim

# 2. Adım: Konteyner içinde çalışacağımız bir klasör oluştur
WORKDIR /app

# 3. Adım: Önce kütüphane listesini konteynere kopyala
COPY requirements.txt .

# 4. Adım: Tüm kütüphaneleri kur
RUN pip install --no-cache-dir -r requirements.txt

# 5. Adım: Projedeki diğer tüm dosyaları (.py, .csv, .json) konteynere kopyala
COPY . .

# 6. Adım: Google Cloud Run'ın beklediği port'u dışarıya aç
EXPOSE 8080

# 7. Adım: Konteyner çalıştığında Streamlit'i başlatacak olan komut
CMD ["streamlit", "run", "app.py", "--server.port=8080", "--server.enableCORS=false", "--server.headless=true"]
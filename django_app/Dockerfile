# 1. Базовый образ с Python 3.10
FROM python:3.12.3

# 2. Отключаем создание pyc-файлов и буферизацию вывода
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# 3. Рабочая директория внутри контейнера
WORKDIR /app

# 4. Копируем файл с зависимостями и устанавливаем их
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r /app/requirements.txt

# 5. Копируем весь исходный код проекта, включая .env
COPY . /app

# 6. Делаем entrypoint.sh исполняемым
RUN chmod +x /app/entrypoint.sh

# 7. Открываем порт Django
EXPOSE 8000

# 8. Точка входа — запускаем entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]

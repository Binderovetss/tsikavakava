# Используем Python 3.10
FROM python:3.10

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем ВСЕ файлы проекта в контейнер
COPY . /app

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r /app/requirements.txt

# Запускаем бота
CMD ["python", "/app/bot.py"]
# استفاده از تصویر رسمی پایتون
FROM python:3.13.0-slim

# تنظیم محیط کار
WORKDIR /app

# نصب وابستگی‌ها
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# کپی پروژه
COPY . .

# اجرای migrations و جمع‌آوری فایل‌های استاتیک
RUN python manage.py migrate --noinput && \
    python manage.py collectstatic --noinput

# پورت مورد استفاده
EXPOSE 8000

# دستور اجرا
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "myproject.wsgi"]
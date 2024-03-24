FROM python:3.10

COPY /app /app_dock
COPY requirements.txt /app_dock

WORKDIR /app_dock
RUN pip install -r requirements.txt

CMD ["python", "main.py"]
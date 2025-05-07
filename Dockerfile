FROM python:3.8-slim
WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app
EXPOSE 5000
ENV PORT=5000
ENV JWT_SECRET_KEY="a9T3kPzB6L8mQfR2wYdS7nXcE4uJ1oV0"
    CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]

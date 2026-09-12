FROM python:3.12-slim
WORKDIR /app
RUN useradd --create-home --uid 10001 appuser
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY main.py policy.py planner.py world.py ./
USER appuser
EXPOSE 8200
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8200"]

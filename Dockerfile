
FROM python:3.11-slim
RUN pip install numpy pandas matplotlib biopython
WORKDIR /app
COPY . /app
CMD ["python","main.py","--mode","basic"]

FROM python:3.10-slim

WORKDIR /app

COPY . /app

# RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple -r req.txt
RUN apt-get update && apt-get install -y postgresql-client

RUN pip install -r req.txt

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]


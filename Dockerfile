# Get an image from Docker Hub
#Base Image
FROM python:3.10-slim

#Setting the working directory inside the container
WORKDIR /app

#Copying the current directory contents into the container
COPY . /app

#Install dependencies
# RUN pip install --upgrade pip --timeout=600
RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple -r req.txt
RUN pip install -r req.txt

#port on which fastapi will run on
EXPOSE 8000

#Command to run the application on uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]


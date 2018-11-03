FROM python:3.7-stretch
WORKDIR /app/
COPY . /app
RUN pip install --trusted-host pypi.python.org -r /app/requirements.txt
EXPOSE 5000 50051
CMD ["python","/app/app.py"]

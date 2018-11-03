# Command to build Docker image must be run from top level project folder,
# otherwise the contents of the protos folder will not be copied to the image.
# Example: docker build -f ./frontend_server/Dockerfile -t history_frontend .

FROM python:3.7-stretch
WORKDIR /app/
COPY . /app
COPY ./protos/ /app/rpc_classes
RUN pip install --trusted-host pypi.python.org -r /app/requirements.txt
EXPOSE 5000 50051
CMD ["python","/app/app.py"]

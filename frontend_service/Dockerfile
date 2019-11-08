# Command to build Docker image must be run from top level project folder,
# otherwise the contents of the protos folder will not be copied to the image.
# Example: docker build -f ./frontend_server/Dockerfile -t history_frontend .

FROM python:3.8-alpine
WORKDIR /app/
COPY ./frontend_service/ /app/
COPY ./protos/ /app/rpc_classes
RUN pip install --trusted-host pypi.python.org -r /app/requirements.txt
EXPOSE 5000
CMD ["python","/app/app.py"]

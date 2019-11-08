# Command to build Docker image must be run from top level project folder,
# otherwise the contents of the protos folder will not be copied to the image.
# Example: docker build -f ./events_rpc_server/Dockerfile -t history_rpc .

FROM python:3.8-alpine
WORKDIR /app/
COPY ./events_rpc_service/ /app/
COPY ./protos/ /app/rpc_classes
RUN pip install --trusted-host pypi.python.org -r /app/requirements.txt
EXPOSE 50051
CMD ["python","/app/events_rpc_server.py"]

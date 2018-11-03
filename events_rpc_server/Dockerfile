FROM grpc/python:latest
WORKDIR /app/
COPY ./events_rpc_server/ /app/
COPY ./protos/ /app/rpc_classes
RUN pip install --trusted-host pypi.python.org -r /app/requirements.txt
EXPOSE 50051
CMD ["python","/app/gcal_events.py"]

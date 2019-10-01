FROM golang:1.13.1
WORKDIR /app
COPY . .
RUN go get github.com/spf13/viper
RUN go build -o main .
EXPOSE 3001
CMD ["./main"]
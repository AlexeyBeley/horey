FROM golang:1.25-alpine AS builder

WORKDIR /app
COPY go.mod ./
COPY main.go ./
RUN go mod tidy
RUN CGO_ENABLED=0 GOOS=linux go build -o socks5-proxy

FROM alpine:latest
RUN apk --no-cache add ca-certificates
WORKDIR /root/
COPY --from=builder /app/socks5-proxy .
EXPOSE 1080
CMD ["./socks5-proxy"]

# docker build -t socks5-proxy .
# docker run -p 1080:1080 socks5-proxy

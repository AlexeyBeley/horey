package main

import (
	"log"
	"net"

	"github.com/armon/go-socks5"
)

func main() {
	conf := &socks5.Config{}
	server, err := socks5.New(conf)
	if err != nil {
		log.Fatal(err)
	}

	listener, err := net.Listen("tcp", ":1080")
	if err != nil {
		log.Fatal(err)
	}

	log.Println("SOCKS5 proxy listening on :1080")
	if err := server.Serve(listener); err != nil {
		log.Fatal(err)
	}
}
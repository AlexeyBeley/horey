package main

import "C"

//export Add
func Add(a, b C.int) C.int {
	return a + b
}

//export Greet
func Greet(name *C.char) *C.char {
	// ... implementation
	return name
}

func main() {}
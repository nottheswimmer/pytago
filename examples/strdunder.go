package main

import "fmt"

type A struct {
	a string
}

func NewA(val string) (self *A) {
	self = new(A)
	self.a = val
	return
}

func (self *A) String() string {
	return self.a
}

func main() {
	val := NewA("ok")
	fmt.Println(val)
}

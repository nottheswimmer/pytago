package main

import "fmt"

type Welcome struct {
	greeting     string
	instructions []string
}

func NewWelcome(greeting string, instructions []string) (self *Welcome) {
	self = new(Welcome)
	self.greeting = greeting
	self.instructions = instructions
	return
}

func (self *Welcome) greet() {
	fmt.Println(self.greeting)
	for _, instruction := range self.instructions {
		fmt.Println(instruction)
	}
}

func main() {
	welcome := NewWelcome(
		"Hello World",
		[]string{
			"This is a class!",
			"Support will be limited at first.",
			"Still, I hope you'll find them useful.",
		},
	)
	welcome.greet()
}

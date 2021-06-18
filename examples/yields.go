package main

import "fmt"

func main() {
	my_gen := gen()
	for x, ok := <-my_gen(); ok; x, ok = <-my_gen() {
		fmt.Println("Received next number!")
		fmt.Println(x)
	}
}

func gen() func() <-chan int {
	wait := make(chan struct{}, 1)
	yield := make(chan int, 1)
	go func() {
		defer close(yield)
		<-wait
		fmt.Println("Yielding next number...")
		yield <- 1
		<-wait
		fmt.Println("Yielding next number...")
		yield <- 2
		<-wait
		fmt.Println("Yielding next number...")
		yield <- 3
		<-wait
	}()
	return func() <-chan int {
		wait <- struct{}{}
		return yield
	}
}

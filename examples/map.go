package main

import "fmt"

func main() {
	a := []int{1, 2, 3}
	b := func() func() <-chan int {
		wait := make(chan struct{})
		yield := make(chan int)
		go func() {
			defer close(yield)
			<-wait
			for _, x := range a {
				yield <- increment(x)
				<-wait
			}
		}()
		return func() <-chan int {
			wait <- struct{}{}
			return yield
		}
	}()
	for value, ok := <-b(); ok; value, ok = <-b() {
		fmt.Println(value)
	}
}

func increment(n int) int {
	return n + 1
}

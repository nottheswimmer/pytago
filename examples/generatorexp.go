package main

import "fmt"

func main() {
	a := func() func() <-chan [2]int {
		wait := make(chan struct{})
		yield := make(chan [2]int)
		go func() {
			defer close(yield)
			<-wait
			for x := 0; x < 5; x++ {
				for y := 0; y < x; y++ {
					yield <- [2]int{x, y}
					<-wait
				}
			}
		}()
		return func() <-chan [2]int {
			wait <- struct{}{}
			return yield
		}
	}()
	b := func() func() <-chan string {
		wait := make(chan struct{})
		yield := make(chan string)
		go func() {
			defer close(yield)
			<-wait
			for _, w := range [7]string{"Where", "Are", "You?", "And", "I'm", "So", "Sorry"} {
				yield <- w
				<-wait
			}
		}()
		return func() <-chan string {
			wait <- struct{}{}
			return yield
		}
	}()
	for l, ok := <-b(); ok; l, ok = <-b() {
		fmt.Println(l, <-a())
	}
	for rest, ok := <-a(); ok; rest, ok = <-a() {
		fmt.Println(rest)
	}
}

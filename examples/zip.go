package main

import "fmt"

func main() {
	x := []int{1, 2, 3}
	y := []int{4, 5, 6}
	zipped := func() func() <-chan [2]int {
		wait := make(chan struct{})
		yield := make(chan [2]int)
		go func() {
			defer close(yield)
			<-wait
			for i, e := range x {
				if i >= len(y) {
					break
				}
				yield <- [2]int{e, y[i]}
				<-wait
			}
		}()
		return func() <-chan [2]int {
			wait <- struct{}{}
			return yield
		}
	}()
	for pair, ok := <-zipped(); ok; pair, ok = <-zipped() {
		fmt.Println(pair)
	}
}

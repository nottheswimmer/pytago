package main

import (
	"fmt"
	"time"
)

func myAsyncFunction() <-chan int {
	r := make(chan int)
	go func() {
		defer close(r)
		time.Sleep(time.Second * 2)
		r <- 2
	}()
	return r
}

func main() {
	r := <-myAsyncFunction()
	fmt.Println(r)
}

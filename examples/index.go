package main

import (
	"errors"
	"fmt"
)

func main() {
	x := []int{1, 2, 3, 7, 3}
	fmt.Println(func() int {
		for i, val := range x {
			if val == 7 {
				return i
			}
		}
		panic(errors.New("ValueError"))
	}())
}

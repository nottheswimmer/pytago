package main

import "fmt"

func main() {
	fmt.Println(func() (s int) {
		for _, e := range []int{1, 2, 3} {
			s += e
		}
		return
	}())
	fmt.Println(func() (s float64) {
		for _, e := range []float64{1.5, 2.6, 3.7} {
			s += e
		}
		return
	}())
	fmt.Println(func() (s complex128) {
		for _, e := range []complex128{1.0i, 2.0i, 3.0i} {
			s += e
		}
		return
	}())
}

package main

import "fmt"

func main() {
	a := func() (d map[[2]int]int) {
		d = make(map[[2]int]int)
		for x := 0; x < 20; x++ {
			for y := 0; y < 5; y++ {
				if x*y != 0 {
					d[[2]int{x, y}] = x * y
				}
			}
		}
		return
	}()
	for k, v := range a {
		fmt.Println(k, v)
	}
}

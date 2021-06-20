package main

import "fmt"

func main() {
	for _, v := range [3][3]int{[3]int{1, 2, 3}, [3]int{4, 5, 6}, [3]int{7, 8, 9}} {
		a, b, c := v[0], v[1], v[2]
		fmt.Println(c, b, a)
	}
}

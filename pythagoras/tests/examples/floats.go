package main

import "fmt"

func main() {
	a := 7
	b := 3
	c := 4.5
	fmt.Println(float64(a) / float64(b))
	fmt.Println(a / b)
	fmt.Println(float64(a) / c)
	fmt.Println(float64(a / int(c)))
	fmt.Println(a + b)
	fmt.Println(float64(a) + c)
}

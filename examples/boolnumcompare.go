package main

import "fmt"

func main() {
	fmt.Println(1 == 1)
	fmt.Println(1 == 0)
	fmt.Println(0 == 1)
	fmt.Println(0 == 0)
	fmt.Println()
	fmt.Println(1.0 == 1)
	fmt.Println(1.0 == 0)
	fmt.Println(0.0 == 1)
	fmt.Println(0.0 == 0)
	fmt.Println()
	fmt.Println(1+0.0i == 1)
	fmt.Println(1+0.0i == 0)
	fmt.Println(0+0.0i == 1)
	fmt.Println(0+0.0i == 0)
	fmt.Println()
	fmt.Println(2 == 1)
}

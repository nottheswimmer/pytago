package main

import "fmt"

func main() {
	a := 1
	switch a {
	case 1:
		fmt.Println(1)
	case 2:
		fmt.Println(2)
	case 3:
		fmt.Println(3)
	}
	switch a {
	case 4:
		fmt.Println("Never gonna happen")
	default:
		fmt.Println("Nice, defaults!")
	}
}

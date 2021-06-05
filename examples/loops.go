package main

import "fmt"

func main() {
	a := []int{1, 2, 3}
	for _, v := range a {
		fmt.Println(v)
	}
	for i, v := range a {
		fmt.Println(i + v)
	}
	for i := 0; i < 5; i++ {
		fmt.Println(i)
	}
	for i := 10; i < 15; i++ {
		fmt.Println(i)
	}
	for i := 10; i < 15; i += 2 {
		fmt.Println(i)
	}
	for j := 15; j > 10; j-- {
		fmt.Println(j)
	}
	for j := 15; j > 10; j -= 2 {
		fmt.Println(j)
	}
}

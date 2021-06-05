package main

import "fmt"

func main() {
	a := []int{1, 2, 3}
	fmt.Println(a[0])
	fmt.Println(a[1])
	fmt.Println(a[2])
	a = append(a, 4)
	fmt.Println(a[3])
	a = append(a, []int{5, 6, 7}...)
	fmt.Println(a[4])
	fmt.Println(a[len(a)-1])
}

package main

import "fmt"

func main() {
	nums := []int{1, 2, 3, 4, 5, 6, 7, 8, 9}
	s := fmt.Sprintf("%#v", nums)
	fmt.Println(s + s)
}

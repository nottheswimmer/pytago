package main

import "fmt"

func main() {
	a := []int{1, 2, 3, 4, 5}
	for _, x := range func(arr []int) []int {
		arr2 := make([]int, len(arr))
		for i, e := range arr {
			arr2[len(arr)-i-1] = e
		}
		return arr2
	}(a) {
		fmt.Println(x)
	}
	for _, x := range a {
		fmt.Println(x)
	}
	func(arr []int) {
		for i, j := 0, len(arr)-1; i < j; i, j = i+1, j-1 {
			arr[i], arr[j] = arr[j], arr[i]
		}
	}(a)
	for _, x := range a {
		fmt.Println(x)
	}
}

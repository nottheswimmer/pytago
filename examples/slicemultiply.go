package main

import "fmt"

func main() {
	n := 3
	x := func(repeated []int, n int) (result []int) {
		for i := 0; i < n; i++ {
			result = append(result, repeated...)
		}
		return result
	}([]int{1, 2, 3}, n)
	x = func(repeated []int, n int) (result []int) {
		for i := 0; i < n; i++ {
			result = append(result, repeated...)
		}
		return result
	}(x, 3)
	x = func(repeated []int, n int) (result []int) {
		for i := 0; i < n; i++ {
			result = append(result, repeated...)
		}
		return result
	}(x, 3)
	fmt.Println(len(x), x)
}

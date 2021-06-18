package main

import "fmt"

func majorityElement(nums []int) int {
	element, cnt := 0, 0
	for _, e := range nums {
		if element == e {
			cnt += 1
		} else if cnt == 0 {
			element, cnt = e, 1
		} else {
			cnt -= 1
		}
	}
	return element
}

func main() {
	fmt.Println(majorityElement([]int{3, 2, 3}))
	fmt.Println(majorityElement([]int{2, 2, 1, 1, 1, 2, 2}))
}

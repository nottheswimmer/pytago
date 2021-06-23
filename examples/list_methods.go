package main

import (
	"errors"
	"fmt"
	"reflect"
	"sort"
)

func main() {
	l1 := []int{1}
	l2 := []string{"hello", "how", "are", "you?"}
	l3 := []float64{6.2, 1.6, 1.2, 20.1}
	l1 = append(l1, 2)
	fmt.Println(l1)
	l1 = append(l1, []int{4, 5}...)
	fmt.Println(l1)
	l1 = append(l1, 3)
	copy(l1[3+1:], l1[3:])
	l1[3] = 3
	fmt.Println(l1)
	fmt.Println(func() int {
		for i, val := range l1 {
			if val == 2 {
				return i
			}
		}
		panic(errors.New("ValueError: element not found"))
	}())
	fmt.Println(func() int {
		n := 0
		for _, v := range l1 {
			if v == 3 {
				n += 1
			}
		}
		return n
	}())
	func(s *[]int, x int) {
		for i, val := range *s {
			if reflect.DeepEqual(val, x) {
				*s = append((*s)[:i], (*s)[i+1:]...)
				return
			}
		}
		panic(errors.New("ValueError: element not found"))
	}(&l1, 3)
	fmt.Println(l1)
	for len(l1) != 0 {
		fmt.Println(func(s *[]int) int {
			i := len(*s) - 1
			popped := (*s)[i]
			*s = (*s)[:i]
			return popped
		}(&l1))
	}
	l3 = nil
	fmt.Println(l3)
	sort.Ints(l1)
	fmt.Println(l1)
	sort.Strings(l2)
	fmt.Println(l2)
	sort.Float64s(l3)
	fmt.Println(l3)
	func(arr []string) {
		for i, j := 0, len(arr)-1; i < j; i, j = i+1, j-1 {
			arr[i], arr[j] = arr[j], arr[i]
		}
	}(l2)
	fmt.Println(l2)
}

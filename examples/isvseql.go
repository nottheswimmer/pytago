package main

import (
	"fmt"
	"reflect"
)

func main() {
	a := []int{1, 2, 3}
	b := []int{1, 2, 3}
	fmt.Println(reflect.DeepEqual(a, b))
	fmt.Println(!reflect.DeepEqual(a, b))
	fmt.Println(&a == &a)
	fmt.Println(&a == &b)
	fmt.Println(&a != &a)
	fmt.Println(&a != &b)
}

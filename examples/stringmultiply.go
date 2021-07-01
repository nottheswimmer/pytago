package main

import (
	"fmt"
	"strings"
)

func main() {
	s := "1, 2, 3, 4"
	x := strings.Repeat(s, 5)
	y := strings.Repeat(fmt.Sprintf("%v", map[interface{}]struct{}{1: {}, 2: {}, 3: {}, 4: {}}), 6)
	z := strings.Repeat(fmt.Sprintf("%v", []int{1, 2, 3, 4}), 7)
	a := strings.Repeat(fmt.Sprintf("%v", map[interface{}]interface{}{1: 2, 3: 4}), 8)
	b := strings.Repeat(fmt.Sprintf("%v", [4]int{1, 2, 3, 4}), 9)
	c := strings.Repeat("1, 2, 3, 4", 10)
	d := strings.Repeat(strings.TrimSpace("  1, 2, 3, 4  "), 11)
	fmt.Println(x, y, z, a, b, c, d)
}

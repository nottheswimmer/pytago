package main

import (
	"fmt"
	"strings"
)

func main() {
	name := "Michael Wayne Phelps"
	first, middle, last := func(s []string) (string, string, string) {
		return s[0], s[1], s[2]
	}(strings.Fields(name))
	x := []int{1, 2, 3}
	a, b, c := x[0], x[1], x[2]
	d, e, f := 4, 5, 6
	g, h, i := 7, 8, 9
	fmt.Println(first, middle, last, a, b, c, d, e, f, g, h, i)
}

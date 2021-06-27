package main

import "fmt"

func main() {
	a := []int{}
	a = append(a, 3)
	b := []int{}
	b = append(b, a...)
	c := map[string]int{}
	c["hello"] = 1
	d := map[interface{}]interface{}{}
	d[1] = 2
	d["gonna_be_an_interface"] = "yup"
	e := map[int]struct{}{}
	e[1] = struct{}{}
	f := [][]int{{}}
	f[0] = append(f[0], 1)
	g := map[[2]int]int{}
	g[[2]int{1, 2}] = 3
	fmt.Println(a, b, c, d, e, f, g)
}

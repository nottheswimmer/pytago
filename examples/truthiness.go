package main

import "fmt"

func main() {
	if a := 1; a != 0 {
		fmt.Println(a)
	}
	if c := ""; len(c) != 0 {
		fmt.Println(c)
	}
	if d := []byte(""); len(d) != 0 {
		fmt.Println(d)
	}
	if e := "Hello"; len(e) != 0 {
		fmt.Println(e)
	}
	if f := []byte("Goodbye"); len(f) != 0 {
		fmt.Println(f)
	}
	if g := 1.0; g != 0 {
		fmt.Println(g)
	}
	if h := 1.0i; h != 0 {
		fmt.Println(h)
	}
	if i := 0.0; i != 0 {
		fmt.Println(i)
	}
	if j := 0.0i; j != 0 {
		fmt.Println(j)
	}
	if k := []interface{}{}; len(k) != 0 {
		fmt.Println(k)
	}
	if l := []int{1, 2, 3}; len(l) != 0 {
		fmt.Println(l)
	}
	if m := true; m {
		fmt.Println(m)
	}
	if n := false; n {
		fmt.Println(n)
	}
	if o := [0]interface{}{}; len(o) != 0 {
		fmt.Println(o)
	}
	if p := [3]int{1, 2, 3}; len(p) != 0 {
		fmt.Println(p)
	}
	if q := map[interface{}]struct{}{}; len(q) != 0 {
		fmt.Println(q)
	}
	if r := map[int]struct{}{1: {}, 2: {}, 3: {}}; len(r) != 0 {
		fmt.Println(r)
	}
	if s := map[interface{}]interface{}{}; len(s) != 0 {
		fmt.Println(s)
	}
	if t := map[int]int{1: 2}; len(t) != 0 {
		fmt.Println(t)
	}
}

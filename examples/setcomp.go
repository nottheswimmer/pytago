package main

import "fmt"

func main() {
	a := func() (s map[int]struct{}) {
		s = make(map[int]struct{})
		for x := 20; x < 39; x++ {
			s[x] = struct{}{}
		}
		return
	}()
	b := func() (s map[[2]int]struct{}) {
		s = make(map[[2]int]struct{})
		for x := 0; x < 100; x++ {
			for y := x; y < x+5; y++ {
				if func() bool {
					_, ok := a[x%39]
					return ok
				}() {
					s[[2]int{x, y}] = struct{}{}
				}
			}
		}
		return
	}()
	fmt.Println(a)
	fmt.Println(b)
}

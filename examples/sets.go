package main

import "fmt"

func main() {
	s := map[interface{}]struct{}{1: {}, 2: {}, 3: {}}
	x := 1
	fmt.Println(len(s))
	fmt.Println(func() bool {
		_, ok := s[x]
		return ok
	}())
	fmt.Println(!func() bool {
		_, ok := s[x]
		return ok
	}())
}

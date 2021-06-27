package main

import "fmt"

func main() {
	a := map[int]struct{}{1: {}, 2: {}, 3: {}, 4: {}}
	b := map[int]struct{}{4: {}, 5: {}, 6: {}}
	b[7] = struct{}{}
	fmt.Println(func(s1 map[int]struct{}, s2 map[int]struct{}) map[interface{}]struct{} {
		union := map[interface{}]struct{}{}
		for elt := range s1 {
			union[elt] = struct{}{}
		}
		for elt := range s2 {
			union[elt] = struct{}{}
		}
		return union
	}(a, b))
	fmt.Println(func(s1 map[int]struct{}, s2 map[int]struct{}) map[interface{}]struct{} {
		intersection := map[interface{}]struct{}{}
		for elt := range s1 {
			if func() bool {
				_, ok := s2[elt]
				return ok
			}() {
				intersection[elt] = struct{}{}
			}
		}
		return intersection
	}(a, b))
	fmt.Println(func(s1 map[int]struct{}, s2 map[int]struct{}) map[interface{}]struct{} {
		difference := map[interface{}]struct{}{}
		for elt := range s1 {
			if !func() bool {
				_, ok := s2[elt]
				return ok
			}() {
				difference[elt] = struct{}{}
			}
		}
		return difference
	}(a, b))
	fmt.Println(func(s1 map[int]struct{}, s2 map[int]struct{}) map[interface{}]struct{} {
		symmetric_difference := map[interface{}]struct{}{}
		for elt := range s1 {
			if !func() bool {
				_, ok := s2[elt]
				return ok
			}() {
				symmetric_difference[elt] = struct{}{}
			}
		}
		for elt := range s2 {
			if !func() bool {
				_, ok := s1[elt]
				return ok
			}() {
				symmetric_difference[elt] = struct{}{}
			}
		}
		return symmetric_difference
	}(a, b))
	fmt.Println(func(s1 map[int]struct{}, s2 map[int]struct{}) bool {
		for elt := range s1 {
			if !func() bool {
				_, ok := s2[elt]
				return ok
			}() {
				return false
			}
		}
		return true
	}(a, b))
	fmt.Println(func(s1 map[int]struct{}, s2 map[int]struct{}) bool {
		for elt := range s2 {
			if !func() bool {
				_, ok := s1[elt]
				return ok
			}() {
				return false
			}
		}
		return true
	}(a, b))
}

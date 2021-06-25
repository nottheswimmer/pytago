package main

import "fmt"

func main() {
	a := map[interface{}]struct{}{1: {}, 2: {}, 3: {}, 4: {}}
	b := map[interface{}]struct{}{4: {}, 5: {}, 6: {}}
	b[7] = struct{}{}
	fmt.Println(func(s1 map[interface{}]struct{}, s2 map[interface{}]struct{}) map[interface{}]struct{} {
		union := map[interface{}]struct{}{}
		for elt := range s1 {
			union[elt] = struct{}{}
		}
		for elt := range s2 {
			union[elt] = struct{}{}
		}
		return union
	}(a, b))
	fmt.Println(func(s1 map[interface{}]struct{}, s2 map[interface{}]struct{}) map[interface{}]struct{} {
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
	fmt.Println(func(s1 map[interface{}]struct{}, s2 map[interface{}]struct{}) map[interface{}]struct{} {
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
	fmt.Println(func(s1 map[interface{}]struct{}, s2 map[interface{}]struct{}) map[interface{}]struct{} {
		symmetric_intersection := map[interface{}]struct{}{}
		for elt := range s1 {
			if !func() bool {
				_, ok := s2[elt]
				return ok
			}() {
				symmetric_intersection[elt] = struct{}{}
			}
		}
		for elt := range s2 {
			if !func() bool {
				_, ok := s1[elt]
				return ok
			}() {
				symmetric_intersection[elt] = struct{}{}
			}
		}
		return symmetric_intersection
	}(a, b))
	fmt.Println(func(s1 map[interface{}]struct{}, s2 map[interface{}]struct{}) bool {
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
	fmt.Println(func(s1 map[interface{}]struct{}, s2 map[interface{}]struct{}) bool {
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

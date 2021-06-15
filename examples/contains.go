package main

import (
	"bytes"
	"fmt"
	"strings"
)

func main() {
	a := []int{1, 2, 3}
	fmt.Println(func() int {
		for i, v := range a {
			if v == 1 {
				return i
			}
		}
		return -1
	}() != -1)
	fmt.Println(func() int {
		for i, v := range a {
			if v == 4 {
				return i
			}
		}
		return -1
	}() != -1)
	fmt.Println(func() int {
		for i, v := range a {
			if v == 5 {
				return i
			}
		}
		return -1
	}() == -1)
	b := "hello world"
	fmt.Println(strings.Contains(b, "hello"))
	fmt.Println(!strings.Contains(b, "Hello"))
	c := map[interface{}]interface{}{"hello": 1, "world": 2}
	fmt.Println(func() bool {
		_, ok := c["hello"]
		return ok
	}())
	fmt.Println(!func() bool {
		_, ok := c["Hello"]
		return ok
	}())
	d := []byte("hello world")
	fmt.Println(bytes.Contains(d, []byte("hello")))
	fmt.Println(!bytes.Contains(d, []byte("Hello")))
	e := map[interface{}]struct{}{1: {}, 2: {}, 3: {}, "hello": {}}
	fmt.Println(func() bool {
		_, ok := e["hello"]
		return ok
	}())
	fmt.Println(!func() bool {
		_, ok := e[4]
		return ok
	}())
}

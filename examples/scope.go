package main

import (
	"fmt"
	"math/rand"
	"time"
)

func init() {
	rand.Seed(time.Now().UnixNano())
}

func main() {
	var a int
	var b int
	if rand.Float64() > 0.5 {
		a = 1
	} else {
		a = 2
	}
	if rand.Float64() > 0.5 {
		if rand.Float64() > 0.5 {
			b = 1
		} else {
			b = 2
		}
	} else {
		b = 3
	}
	hello_world := func() {
		c := 3
		fmt.Println(c)
	}
	hello_world()
	fmt.Println(a, b)
}

package main

import (
	"fmt"
	"strings"
)

func main() {
	a := []int{1, 2, 3}
	for index := 0; index < 4; index++ {
		func() {
			defer func() {
				if r := recover(); r != nil {
					if err, ok := r.(error); ok {
						if strings.HasPrefix(err.Error(), "IndexError") || strings.HasPrefix(err.Error(), "runtime error: index out of range") {
							fmt.Println("That index was out of bounds")
							return
						} else if strings.HasPrefix(err.Error(), "NotImplementedError") || (strings.HasPrefix(err.Error(), "RuntimeError") || strings.HasPrefix(err.Error(), "runtime error")) {
							fmt.Println("This won't actually happen...")
							return
						} else {
							e := err
							fmt.Println("Some other exception occurred")
							fmt.Println(e)
							return
						}
					}
					panic(r)
				}
			}()
			fmt.Println(a[index])
			if index == 1 {
				panic(fmt.Errorf("ValueError: %v", index))
			}
		}()
	}
}

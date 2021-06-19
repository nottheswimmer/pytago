package main

import "fmt"

func main() {
	a := func() int {
		if true {
			return 1
		}
		return 2
	}()
	fmt.Println(a)
}

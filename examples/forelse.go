package main

import "fmt"

func main() {
	var x int
	if func() bool {
		for x = 0; x < 4; x++ {
			if x == 5 {
				return false
			}
		}
		return true
	}() {
		fmt.Println("Well of course that didn't happen")
	}
	if func() bool {
		for x = 0; x < 7; x++ {
			if x == 5 {
				return false
			}
		}
		return true
	}() {
		fmt.Println("H-hey wait!")
	}
	i := 0
	if func() bool {
		for i < 3 {
			fmt.Println("Works with while too")
			for x = 0; x < 3; x++ {
				fmt.Println("BTW don't worry about nested breaks")
				break
			}
			if i == 10 {
				return false
			}
			i += 1
		}
		return true
	}() {
		fmt.Println("Yeah not likely")
	}
	fmt.Println(i)
}

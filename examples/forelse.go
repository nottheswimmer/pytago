package main

import "fmt"

func main() {
	broke := false
	for x := 0; x < 4; x++ {
		if x == 5 {
			broke = true
			break
		}
	}
	if !broke {
		fmt.Println("Well of course that didn't happen")
	}
	broke = false
	for x := 0; x < 7; x++ {
		if x == 5 {
			broke = true
			break
		}
	}
	if !broke {
		fmt.Println("H-hey wait!")
	}
}

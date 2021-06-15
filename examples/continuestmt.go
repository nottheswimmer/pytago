package main

import "fmt"

func main() {
	for i := 0; i < 10; i++ {
		if i < 3 || i > 7 {
			continue
		}
		fmt.Println(i)
	}
}

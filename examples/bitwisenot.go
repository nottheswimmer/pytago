package main

import "fmt"

func main() {
	yeah := 9
	yeah &= ^3
	fmt.Println(yeah)
}

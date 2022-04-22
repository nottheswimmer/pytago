package main

import (
	"fmt"
	"math"
)

func main() {
	fmt.Println(math.Pow(2, 8))
	x := []int{2, 4}
	fmt.Println(math.Pow(float64(x[0]), float64(x[1])))
}

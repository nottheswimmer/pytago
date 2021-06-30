package main

import (
	"fmt"
	"math"
)

func intersection(function func(x float64) float64, x0 float64, x1 float64) float64 {
	x_n := x0
	x_n1 := x1
	for {
		if x_n == x_n1 || function(x_n1) == function(x_n) {
			panic(
				fmt.Errorf("ZeroDivisionError: %v", "float division by zero, could not find root"),
			)
		}
		x_n2 := x_n1 - function(x_n1)/((function(x_n1)-function(x_n))/(x_n1-x_n))
		if math.Abs(x_n2-x_n1) < math.Pow(10, -5) {
			return x_n2
		}
		x_n = x_n1
		x_n1 = x_n2
	}
}

func f(x float64) float64 {
	return math.Pow(x, 3) - float64(2*x) - 5
}

func main() {
	fmt.Println(intersection(f, 3, 3.5))
}

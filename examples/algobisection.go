package main

import (
	"fmt"
	"math"
)

func bisection(function func(x float64) float64, a float64, b float64) float64 {
	start := a
	end := b
	if function(a) == 0 {
		return a
	} else if function(b) == 0 {
		return b
	} else if function(a)*function(b) > 0 {
		panic(fmt.Errorf("ValueError: %v", "could not find root in given interval."))
	} else {
		mid := start + (end-start)/2.0
		for math.Abs(start-mid) > math.Pow(10, -7) {
			if function(mid) == 0 {
				return mid
			} else if function(mid)*function(start) < 0 {
				end = mid
			} else {
				start = mid
			}
			mid = start + (end-start)/2.0
		}
		return mid
	}
}

func f(x float64) float64 {
	return math.Pow(x, 3) - float64(2*x) - 5
}

func main() {
	fmt.Println(bisection(f, 1, 1000))
}

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
	fmt.Println(rand.Float64())
	fmt.Println(func(start int, stop int) int {
		n := stop - start
		return rand.Intn(n) + start
	}(9000, 10000))
	fmt.Println(func(start int, stop int) int {
		n := stop - start
		return rand.Intn(n) + start
	}(9000, 10000+1))
	items := []interface{}{"Hello", 3, "Potato", "Cake"}
	fmt.Println(items[rand.Intn(len(items))])
	rand.Shuffle(len(items), func(i int, j int) {
		items[i], items[j] = items[j], items[i]
	})
	fmt.Println(items)
	u := func(a float64, b float64) float64 {
		return rand.Float64()*(b-a) + b
	}(200, 500)
	fmt.Println(u)
}

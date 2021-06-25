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
	a := rand.Float64()
	fmt.Println(a)
	b := func(start int, stop int) int {
		n := stop - start
		return rand.Intn(n) + start
	}(9000, 10000)
	fmt.Println(b)
	c := func(start int, stop int) int {
		n := stop - start
		return rand.Intn(n) + start
	}(9000, 10000+1)
	fmt.Println(c)
	items := []interface{}{"Hello", 3, "Potato", "Cake"}
	fmt.Println(items[rand.Intn(len(items))])
	rand.Shuffle(len(items), func(i int, j int) {
		items[i], items[j] = items[j], items[i]
	})
	fmt.Println(items)
}

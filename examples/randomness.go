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
	if rand.Float64() > 0.5 {
		fmt.Println("50/50")
	}
	names := []string{
		"Kitchen",
		"Animal",
		"State",
		"Tasty",
		"Big",
		"City",
		"Fish",
		"Pizza",
		"Goat",
		"Salty",
		"Sandwich",
		"Lazy",
		"Fun",
	}
	company_type := []string{"LLC", "Inc", "Company", "Corporation"}
	company_cuisine := []string{
		"Pizza",
		"Bar Food",
		"Fast Food",
		"Italian",
		"Mexican",
		"American",
		"Sushi Bar",
		"Vegetarian",
	}
	for x := 1; x < 501; x++ {
		business := map[string]interface{}{"name": names[func(start int, stop int) int {
			n := stop - start
			return rand.Intn(n) + start
		}(0, len(names)-1+1)] + " " + names[func(start int, stop int) int {
			n := stop - start
			return rand.Intn(n) + start
		}(0, len(names)-1+1)] + " " + company_type[func(start int, stop int) int {
			n := stop - start
			return rand.Intn(n) + start
		}(0, len(company_type)-1+1)], "rating": func(start int, stop int) int {
			n := stop - start
			return rand.Intn(n) + start
		}(1, 5+1), "cuisine": company_cuisine[func(start int, stop int) int {
			n := stop - start
			return rand.Intn(n) + start
		}(0, len(company_cuisine)-1+1)]}
		fmt.Println(business)
	}
}

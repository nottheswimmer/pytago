package main

import "fmt"

var (
	SITE = "https://www.google.com/"
	NAME = []string{"Michael", "Wayne", "Phelps"}
	KEYS = map[interface{}]interface{}{1: 2, 3: 4}
)
var (
	AGE        = 1000
	BIRTH_YEAR = 2050
)

func main() {
	fmt.Println(SITE)
	fmt.Println(NAME)
	fmt.Println(BIRTH_YEAR)
	fmt.Println(KEYS)
	fmt.Println(AGE)
	AGE = 20
	other_1()
	fmt.Println(AGE)
	other_2()
}

func other_1() {
	AGE := 200
	fmt.Println(AGE)
}

func other_2() {
	fmt.Println(AGE)
}

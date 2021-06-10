package main

import "fmt"

func main() {
	a := map[interface{}]interface{}{"name": "Michael", "age": 24, 1337: true}
	fmt.Println(a)
	a["sleepiness"] = 1.0
	delete(a, 1337)
	for k, v := range a {
		fmt.Println(k)
		fmt.Println(v)
	}
}

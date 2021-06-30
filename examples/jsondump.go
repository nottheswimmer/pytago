package main

import (
	"encoding/json"
	"fmt"
)

func main() {
	fmt.Println(func() string {
		b, err := json.Marshal(1)
		if err != nil {
			panic(err)
		}
		return string(b)
	}())
	fmt.Println(func() string {
		b, err := json.Marshal("hello")
		if err != nil {
			panic(err)
		}
		return string(b)
	}())
	c := func() string {
		b, err := json.Marshal(map[string]interface{}{"hello": 1, "how": "are you"})
		if err != nil {
			panic(err)
		}
		return string(b)
	}()
	fmt.Println(c + c)
	fmt.Println(func() string {
		b, err := json.Marshal([]int{1, 2, 3})
		if err != nil {
			panic(err)
		}
		return string(b)
	}())
}

package main

import "fmt"

func main() {
	a := []interface{}{"a", 1, "5", 2.3, 1.2i}
	some_condition := true
	for _, x := range a {
		switch x.(type) {
		case string, float64:
			fmt.Println("String or float!")
		case int:
			fmt.Println("Integer!")
		default:
			fmt.Println("Dunno!")
			fmt.Println(":)")
		}
		if func() bool {
			switch x.(type) {
			case string:
				return true
			}
			return false
		}() && some_condition {
			fmt.Println("String")
		} else {
			switch x.(type) {
			case int:
				fmt.Println("Integer!")
			default:
				fmt.Println("Dunno!!")
				fmt.Println(":O")
			}
		}
	}
}

package main

import "fmt"

func main() {
	a := []int{1, 2, 3}
	for index := 0; index < 4; index++ {
		func() {
			defer func() {
				fmt.Println("Finished an iteration")
			}()
			defer func() {
				if r := recover(); r != nil {
					if _, ok := r.(error); ok {
						return
					}
					panic(r)
				}
			}()
			fmt.Println(a[index])
		}()
	}
	for index := 0; index < 4; index++ {
		func() {
			defer func() {
				fmt.Println("Finished an iteration")
			}()
			fmt.Println(a[index])
		}()
	}
}

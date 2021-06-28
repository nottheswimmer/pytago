package main

import (
	"fmt"
	"os"
)

func main() {
	stuff := []interface{}{1, 5, "hello", 5, 12, 19, 12.5, []int{1, 2, 3}}
	write_contents(stuff)
	items := []interface{}{"", 0, 1.1}
	for _, x := range items {
		switch x.(type) {
		case string:
			fmt.Println("See? It's not used here so we don't have a type assertion")
		case int:
			fmt.Println("This is very important because go's compiler will complain")
		default:
			fmt.Println("You know, I wouldn't have to worry about this if we had something to remove unused initializations")
		}
	}
}

func write_contents(contents []interface{}) {
	f := func() *os.File {
		f, err := os.OpenFile("contents.txt", os.O_RDWR|os.O_TRUNC|os.O_CREATE, 0o777)
		if err != nil {
			panic(err)
		}
		return f
	}()
	defer func() {
		if err := f.Close(); err != nil {
			panic(err)
		}
	}()
	for _, item := range contents {
		switch item := item.(type) {
		case string:
			func() int {
				n, err := f.WriteString("str: " + item + "\n")
				if err != nil {
					panic(err)
				}
				return n
			}()
		case int:
			func() int {
				n, err := f.WriteString("int: " + fmt.Sprintf("%v", item) + "\n")
				if err != nil {
					panic(err)
				}
				return n
			}()
		default:
			func() int {
				n, err := f.WriteString("unknown: " + fmt.Sprintf("%#v", item) + "\n")
				if err != nil {
					panic(err)
				}
				return n
			}()
		}
	}
}

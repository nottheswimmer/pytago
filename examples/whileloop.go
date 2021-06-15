package main

import "fmt"

func main() {
	i := 0
	for {
		fmt.Println(i)
		i += 1
		if i > 5 {
			break
		}
	}
	j := 10
	for j < 100 {
		fmt.Println(j)
		j += 10
	}
	for {
		fmt.Println(j + i)
		break
	}
	for {
		fmt.Println(j + i)
		break
	}
	for false {
		fmt.Println("This never executes")
	}
	for false {
		fmt.Println("This never executes")
	}
	for false {
		fmt.Println("This never executes")
	}
	for false {
		fmt.Println("This never executes")
	}
	for false {
		fmt.Println("This never executes")
	}
	for {
		fmt.Println("This executes")
		break
	}
}

package main

import "fmt"

func main() {
	if a := some_func(); a == 7 {
		fmt.Println(a)
	}
	y := []int{1, 2, 3}
	for _, x := range y {
		fmt.Println(y)
		fmt.Println(x)
	}
	switch j := 5; j {
	case 5:
		fmt.Println(j)
	}
	for t1, t2 := thing_1(), thing_2(); t1 < 5 && t2 == 3; t1, t2 = thing_1(), thing_2() {
		fmt.Println(t1)
		fmt.Println(t2)
	}
}

func some_func() int {
	return 7
}

var call_count = 0

func thing_1() int {
	call_count += 1
	return call_count
}

func thing_2() int {
	return 3
}

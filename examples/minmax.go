package main

import "fmt"

func main() {
	fmt.Println(func() (m int) {
		for i, e := range []int{1, 2, 3} {
			if i == 0 || e > m {
				m = e
			}
		}
		return
	}())
	fmt.Println(func() (m int) {
		for i, e := range []int{1, 2, 3} {
			if i == 0 || e < m {
				m = e
			}
		}
		return
	}())
	fmt.Println(func() (m string) {
		for i, e := range []string{"a", "b", "c"} {
			if i == 0 || e > m {
				m = e
			}
		}
		return
	}())
	fmt.Println(func() (m string) {
		for i, e := range []string{"a", "b", "c"} {
			if i == 0 || e < m {
				m = e
			}
		}
		return
	}())
}

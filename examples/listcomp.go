package main

import "fmt"

func main() {
	a := func() (elts []int) {
		for x := 0; x < 10; x++ {
			elts = append(elts, x)
		}
		return
	}()
	b := func() (elts []int) {
		for x := 0; x < 10; x++ {
			if x%2 == 0 {
				elts = append(elts, x)
			}
		}
		return
	}()
	c := func() (elts []int) {
		for x := 0; x < 10; x++ {
			elts = append(elts, func() int {
				if x%2 == 0 {
					return x
				}
				return 777
			}())
		}
		return
	}()
	d := func() (elts []int) {
		for i, x := range c {
			if i%2 == 0 {
				if i%3 == 1 {
					elts = append(elts, x)
				}
			}
		}
		return
	}()
	e := func() (elts [][]int) {
		for _, x := range c {
			for _, y := range d {
				elts = append(elts, []int{x, y})
			}
		}
		return
	}()
	f := func() (elts [][]int) {
		for _, x := range c {
			for _, y := range next_five_numbers_times_two(x) {
				elts = append(elts, []int{x, y})
			}
		}
		return
	}()
	g := func() (elts [][]int) {
		for i := 0; i < 10; i++ {
			for j := 0; j < i; j++ {
				elts = append(elts, []int{i, j})
			}
		}
		return
	}()
	fmt.Println(a)
	fmt.Println(b)
	fmt.Println(c)
	fmt.Println(d)
	fmt.Println(e)
	fmt.Println(f)
	fmt.Println(g)
}

func next_five_numbers_times_two(a int) []int {
	return func() (elts []int) {
		for i := 1; i < 6; i++ {
			elts = append(elts, (a+i)*2)
		}
		return
	}()
}

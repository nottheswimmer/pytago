package main

import "fmt"

var (
	A = []int{1, 2, 3}
	B int
	C int
	D int
)

func init() {
	for i, x := range A {
		A[i] += x
	}
	B = A[0]
	C = A[0]
	D = 3
	for C < A[2] {
		C += 1
	}
	if C == A[2] {
		fmt.Println("True")
	}
}

func main() {
	fmt.Println("Main started")
	fmt.Println(A)
	fmt.Println(B)
	fmt.Println(C)
	fmt.Println(D)
}

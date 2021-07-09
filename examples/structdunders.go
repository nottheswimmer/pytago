package main

import "fmt"

type Number struct {
	x int
}

func NewNumber(x int) (self *Number) {
	self = new(Number)
	self.x = x
	return
}

func (self *Number) Add(other Number) *Number {
	return NewNumber(self.x + other.x)
}

func (self *Number) Mul(other Number) *Number {
	return NewNumber(self.x * other.x)
}

func (self *Number) String() string {
	return fmt.Sprintf("%v", self.x)
}

type ComplexNumber struct {
	real *Number
	imag *Number
}

func NewComplexNumber(real *Number, imag *Number) (self *ComplexNumber) {
	self = new(ComplexNumber)
	self.real = real
	self.imag = imag
	return
}

func (self *ComplexNumber) String() string {
	return fmt.Sprintf("%v", self.real) + "+" + fmt.Sprintf("%v", self.imag) + "i"
}

func main() {
	five := NewNumber(5)
	six := NewNumber(6)
	eleven := five.Add(*six)
	fmt.Println(eleven)
	fifty_five := five.Mul(*eleven)
	fmt.Println(fifty_five)
	i := NewComplexNumber(NewNumber(0), NewNumber(-1))
	n := NewComplexNumber(NewNumber(3), NewNumber(-6))
	fmt.Println(i, n)
}

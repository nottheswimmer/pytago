package main

import (
	"errors"
	"fmt"
)

func main() {
	if !(1+1 == 2) {
		panic(errors.New("AssertionError"))
	}
	if !true {
		panic(errors.New("AssertionError"))
	}
	if !(1+3 == 5) {
		panic(fmt.Errorf("AssertionError: %v", "Math must be broken"))
	}
}

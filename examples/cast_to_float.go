package main

import (
	"bufio"
	"fmt"
	"os"
	"strconv"
	"strings"
)

func main() {
	num1 := func(msg string) string {
		fmt.Print(msg)
		text, _ := bufio.NewReader(os.Stdin).ReadString('\n')
		return strings.ReplaceAll(text, "\n", "")
	}("Enter first number: ")
	num2 := func(msg string) string {
		fmt.Print(msg)
		text, _ := bufio.NewReader(os.Stdin).ReadString('\n')
		return strings.ReplaceAll(text, "\n", "")
	}("Enter second number: ")
	sum := func() float64 {
		i, err := strconv.ParseFloat(num1, 64)
		if err != nil {
			panic(err)
		}
		return i
	}() + func() float64 {
		i, err := strconv.ParseFloat(num2, 64)
		if err != nil {
			panic(err)
		}
		return i
	}()
	fmt.Println("The sum of", num1, "and", num2, "is", sum)
}

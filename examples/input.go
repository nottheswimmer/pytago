package main

import (
	"bufio"
	"fmt"
	"os"
	"strconv"
	"strings"
)

func main() {
	fmt.Println("Hi, what's your name?")
	name := func(msg string) string {
		reader := bufio.NewReader(os.Stdin)
		fmt.Print(msg)
		text, _ := reader.ReadString('\n')
		return strings.ReplaceAll(text, "\n", "")
	}("Name: ")
	fmt.Println("Hi", name, "how old are you?")
	age := func() int {
		i, err := strconv.ParseInt(func(msg string) string {
			reader := bufio.NewReader(os.Stdin)
			fmt.Print(msg)
			text, _ := reader.ReadString('\n')
			return strings.ReplaceAll(text, "\n", "")
		}("Age: "), 10, 64)
		if err != nil {
			panic(err)
		}
		return int(i)
	}()
	fmt.Println("Describe yourself in one sentence:")
	description := func() string {
		reader := bufio.NewReader(os.Stdin)
		text, _ := reader.ReadString('\n')
		return strings.ReplaceAll(text, "\n", "")
	}()
	fmt.Println("So your name is", name, "and you are", age, "years old, and your description is", "\""+description+"\"")
}

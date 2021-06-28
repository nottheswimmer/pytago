package main

import (
	"bufio"
	"fmt"
	"os"
)

func main() {
	fh := func() *os.File {
		f, err := os.OpenFile("file.txt", os.O_RDONLY, 0o777)
		if err != nil {
			panic(err)
		}
		return f
	}()
	if sc := bufio.NewScanner(fh); sc.Scan() {
		for line, more, done := sc.Text(), sc.Scan(), false; !done; line, more, done = sc.Text(), sc.Scan(), !more {
			fmt.Println(line)
		}
	}
	func(obj *os.File) {
		err := obj.Close()
		if err != nil {
			panic(err)
		}
	}(fh)
	func() {
		fh2 := func() *os.File {
			f, err := os.OpenFile("file2.txt", os.O_RDONLY, 0o777)
			if err != nil {
				panic(err)
			}
			return f
		}()
		defer func() {
			if err := fh2.Close(); err != nil {
				panic(err)
			}
		}()
		if sc := bufio.NewScanner(fh2); sc.Scan() {
			for line, more, done := sc.Text(), sc.Scan(), false; !done; line, more, done = sc.Text(), sc.Scan(), !more {
				fmt.Println(line)
			}
		}
	}()
}

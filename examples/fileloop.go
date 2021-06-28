package main

import (
	"bufio"
	"fmt"
	"io"
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
	if sc, line, err := bufio.NewReader(fh), "", *new(error); true {
		for {
			line, err = sc.ReadString('\n')
			if err != nil && (err == io.EOF && len(line) == 0 || err != io.EOF) {
				break
			}
			fmt.Println(line)
		}
		if err != io.EOF {
			panic(err)
		}
	}
	if err := fh.Close(); err != nil {
		panic(err)
	}
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
		if sc, line, err := bufio.NewReader(fh2), "", *new(error); true {
			for {
				line, err = sc.ReadString('\n')
				if err != nil && (err == io.EOF && len(line) == 0 || err != io.EOF) {
					break
				}
				fmt.Println(line)
			}
			if err != io.EOF {
				panic(err)
			}
		}
	}()
	func() {
		fh3 := func() *os.File {
			f, err := os.OpenFile("file3.txt", os.O_RDONLY, 0o777)
			if err != nil {
				panic(err)
			}
			return f
		}()
		defer func() {
			if err := fh3.Close(); err != nil {
				panic(err)
			}
		}()
		if sc, l, err := bufio.NewReader(fh3), []byte{}, *new(error); true {
			for {
				l, err = sc.ReadBytes('\n')
				if err != nil && (err == io.EOF && len(l) == 0 || err != io.EOF) {
					break
				}
				fmt.Println(l)
			}
			if err != io.EOF {
				panic(err)
			}
		}
	}()
}

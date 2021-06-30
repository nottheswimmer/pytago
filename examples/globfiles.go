package main

import (
	"bufio"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"strings"
	"unicode"
)

func main() {
	for _, py_file := range func(pattern string) []string {
		matches, err := filepath.Glob(pattern)
		if err != nil {
			panic(err)
		}
		return matches
	}("./*.py") {
		fmt.Println(strings.Repeat("=", 20), py_file, strings.Repeat("=", 20))
		func() {
			py_f := func() *os.File {
				f, err := os.OpenFile(py_file, os.O_RDONLY, 0o777)
				if err != nil {
					panic(err)
				}
				return f
			}()
			defer func() {
				if err := py_f.Close(); err != nil {
					panic(err)
				}
			}()
			if sc, line, err := bufio.NewReader(py_f), "", *new(error); true {
				for {
					line, err = sc.ReadString('\n')
					if err != nil && (err == io.EOF && len(line) == 0 || err != io.EOF) {
						break
					}
					fmt.Println(strings.TrimRightFunc(line, unicode.IsSpace))
				}
				if err != io.EOF {
					panic(err)
				}
			}
		}()
	}
}

package main

import (
	"fmt"
	"io/ioutil"
	"os"
)

func main() {
	func() {
		f := func() *os.File {
			f, err := os.OpenFile("file_1.tmp", os.O_RDWR|os.O_TRUNC|os.O_CREATE, 0o777)
			if err != nil {
				panic(err)
			}
			return f
		}()
		defer func() {
			if err := f.Close(); err != nil {
				panic(err)
			}
		}()
		func() int {
			n, err := f.WriteString("This file was created in w+ mode\n")
			if err != nil {
				panic(err)
			}
			return n
		}()
	}()
	func() {
		f := func() *os.File {
			f, err := os.OpenFile("file_2.tmp", os.O_WRONLY|os.O_EXCL|os.O_CREATE, 0o777)
			if err != nil {
				panic(err)
			}
			return f
		}()
		defer func() {
			if err := f.Close(); err != nil {
				panic(err)
			}
		}()
		func() int {
			n, err := f.WriteString("This file was created by x mode\n")
			if err != nil {
				panic(err)
			}
			return n
		}()
	}()
	func() {
		f := func() *os.File {
			f, err := os.OpenFile("file_2.tmp", os.O_WRONLY|os.O_TRUNC, 0o777)
			if err != nil {
				panic(err)
			}
			return f
		}()
		defer func() {
			if err := f.Close(); err != nil {
				panic(err)
			}
		}()
		func() int {
			n, err := f.WriteString("This file was created by x mode and then overwritten in w mode\n")
			if err != nil {
				panic(err)
			}
			return n
		}()
	}()
	func() {
		f := func() *os.File {
			f, err := os.OpenFile("file_2.tmp", os.O_WRONLY|os.O_APPEND|os.O_CREATE, 0o777)
			if err != nil {
				panic(err)
			}
			return f
		}()
		defer func() {
			if err := f.Close(); err != nil {
				panic(err)
			}
		}()
		func() int {
			n, err := f.WriteString("... And then appended to in a mode\n")
			if err != nil {
				panic(err)
			}
			return n
		}()
	}()
	func() {
		f := func() *os.File {
			f, err := os.OpenFile("file_2.tmp", os.O_RDONLY, 0o777)
			if err != nil {
				panic(err)
			}
			return f
		}()
		defer func() {
			if err := f.Close(); err != nil {
				panic(err)
			}
		}()
		fmt.Println(func() string {
			content, err := ioutil.ReadAll(f)
			if err != nil {
				panic(err)
			}
			return string(content)
		}())
	}()
	func() {
		f := func() *os.File {
			f, err := os.OpenFile("file_3.tmp", os.O_RDWR|os.O_APPEND|os.O_CREATE, 0o777)
			if err != nil {
				panic(err)
			}
			return f
		}()
		defer func() {
			if err := f.Close(); err != nil {
				panic(err)
			}
		}()
		func() int {
			n, err := f.WriteString("This file was created in a+ mode\n")
			if err != nil {
				panic(err)
			}
			return n
		}()
	}()
	func() {
		f := func() *os.File {
			f, err := os.OpenFile("file_4.tmp", os.O_RDWR|os.O_EXCL|os.O_CREATE, 0o777)
			if err != nil {
				panic(err)
			}
			return f
		}()
		defer func() {
			if err := f.Close(); err != nil {
				panic(err)
			}
		}()
		func() int {
			n, err := f.WriteString("This file was created by x+ mode\n")
			if err != nil {
				panic(err)
			}
			return n
		}()
	}()
	func() {
		f := func() *os.File {
			f, err := os.OpenFile("file_5.tmp", os.O_RDWR|os.O_TRUNC|os.O_CREATE, 0o777)
			if err != nil {
				panic(err)
			}
			return f
		}()
		defer func() {
			if err := f.Close(); err != nil {
				panic(err)
			}
		}()
		func() int {
			n, err := f.Write([]byte("This file was created in wb+ mode\n"))
			if err != nil {
				panic(err)
			}
			return n
		}()
	}()
	func() {
		f := func() *os.File {
			f, err := os.OpenFile("file_6.tmp", os.O_WRONLY|os.O_EXCL|os.O_CREATE, 0o777)
			if err != nil {
				panic(err)
			}
			return f
		}()
		defer func() {
			if err := f.Close(); err != nil {
				panic(err)
			}
		}()
		func() int {
			n, err := f.Write([]byte("This file was created by xb mode\n"))
			if err != nil {
				panic(err)
			}
			return n
		}()
	}()
	func() {
		f := func() *os.File {
			f, err := os.OpenFile("file_6.tmp", os.O_WRONLY|os.O_TRUNC, 0o777)
			if err != nil {
				panic(err)
			}
			return f
		}()
		defer func() {
			if err := f.Close(); err != nil {
				panic(err)
			}
		}()
		func() int {
			n, err := f.Write([]byte("This file was created by xb mode and then overwritten in wb mode\n"))
			if err != nil {
				panic(err)
			}
			return n
		}()
	}()
	func() {
		f := func() *os.File {
			f, err := os.OpenFile("file_6.tmp", os.O_WRONLY|os.O_APPEND|os.O_CREATE, 0o777)
			if err != nil {
				panic(err)
			}
			return f
		}()
		defer func() {
			if err := f.Close(); err != nil {
				panic(err)
			}
		}()
		func() int {
			n, err := f.Write([]byte("... And then appended to in ab mode\n"))
			if err != nil {
				panic(err)
			}
			return n
		}()
	}()
	func() {
		f := func() *os.File {
			f, err := os.OpenFile("file_6.tmp", os.O_RDONLY, 0o777)
			if err != nil {
				panic(err)
			}
			return f
		}()
		defer func() {
			if err := f.Close(); err != nil {
				panic(err)
			}
		}()
		fmt.Println(string(func() []byte {
			content, err := ioutil.ReadAll(f)
			if err != nil {
				panic(err)
			}
			return content
		}()))
	}()
	func() {
		f := func() *os.File {
			f, err := os.OpenFile("file_7.tmp", os.O_RDWR|os.O_APPEND|os.O_CREATE, 0o777)
			if err != nil {
				panic(err)
			}
			return f
		}()
		defer func() {
			if err := f.Close(); err != nil {
				panic(err)
			}
		}()
		func() int {
			n, err := f.Write([]byte("This file was created in ab+ mode\n"))
			if err != nil {
				panic(err)
			}
			return n
		}()
	}()
	func() {
		f := func() *os.File {
			f, err := os.OpenFile("file_8.tmp", os.O_RDWR|os.O_EXCL|os.O_CREATE, 0o777)
			if err != nil {
				panic(err)
			}
			return f
		}()
		defer func() {
			if err := f.Close(); err != nil {
				panic(err)
			}
		}()
		func() int {
			n, err := f.Write([]byte("This file was created by xb+ mode\n"))
			if err != nil {
				panic(err)
			}
			return n
		}()
	}()
}

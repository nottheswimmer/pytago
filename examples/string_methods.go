package main

import (
	"bufio"
	"errors"
	"fmt"
	"strings"
	"unicode"
)

func main() {
	lower := "hello world"
	crazy := "HeLLo WoRlD"
	upper := "HELLO WORLD"
	lol := "---LOL---"
	hearts := "🧡💛💚💙💜"
	arabic_indic_digit := "٠"
	whitespace := " \u000b\f\t\r\n"
	s_hello_s := whitespace + lower + whitespace
	multiline := lower + "\n" + crazy + "\r\n" + upper + "\n"
	fmt.Println(strings.ToUpper(crazy[0:1]) + strings.ToLower(crazy[1:]))
	fmt.Println(strings.HasSuffix(lower, "world"))
	fmt.Println(strings.Index(lower, " "))
	fmt.Println(func() int {
		if r := strings.Index(lower[2:], " "); r != -1 {
			return r + 2
		}
		return -1
	}())
	fmt.Println(func() int {
		if r := strings.Index(upper[7:8], " "); r != -1 {
			return r + 7
		}
		return -1
	}())
	fmt.Println(func(X string, sub string) int {
		if i := strings.Index(X, sub); i != -1 {
			return i
		}
		panic(errors.New("ValueError: substring not found"))
	}(lower, " "))
	fmt.Println(func(X string, sub string, start int) int {
		if i := func() int {
			if r := strings.Index(X[start:], sub); r != -1 {
				return r + start
			}
			return -1
		}(); i != -1 {
			return i
		}
		panic(errors.New("ValueError: substring not found"))
	}(lower, " ", 2))
	fmt.Println(func(X string, sub string, start int, end int) int {
		if i := func() int {
			if r := strings.Index(X[start:end], sub); r != -1 {
				return r + start
			}
			return -1
		}(); i != -1 {
			return i
		}
		panic(errors.New("ValueError: substring not found"))
	}(upper, " ", 2, 8))
	fmt.Println(func(X string) bool {
		for _, r := range X {
			if !((unicode.IsLetter(r) || unicode.IsDigit(r)) && (unicode.IsDigit(r) || unicode.IsNumber(r))) {
				return false
			}
		}
		return true
	}(lower))
	fmt.Println(func(X string) bool {
		for _, r := range X {
			if r > unicode.MaxASCII {
				return false
			}
		}
		return len(X) != 0
	}(hearts))
	fmt.Println(func(X string) bool {
		for _, r := range X {
			if !unicode.Is(unicode.Nd, r) {
				return false
			}
		}
		return len(X) != 0
	}(arabic_indic_digit))
	fmt.Println(func(X string) bool {
		for _, r := range X {
			if !unicode.IsDigit(r) {
				return false
			}
		}
		return len(X) != 0
	}(arabic_indic_digit))
	fmt.Println(func(X string) bool {
		lower_found := false
		for _, r := range X {
			if !unicode.IsLower(r) {
				if !unicode.IsSpace(r) {
					return false
				}
			} else {
				lower_found = true
			}
		}
		return lower_found && len(X) != 0
	}(lower))
	fmt.Println(func(X string) bool {
		for _, r := range X {
			if !(unicode.IsDigit(r) || unicode.IsNumber(r)) {
				return false
			}
		}
		return len(X) != 0
	}(arabic_indic_digit))
	fmt.Println(func(X string) bool {
		for _, r := range X {
			if !unicode.IsPrint(r) {
				return false
			}
		}
		return len(X) != 0
	}(hearts))
	fmt.Println(func(X string) bool {
		for _, r := range X {
			if !unicode.IsSpace(r) {
				return false
			}
		}
		return len(X) != 0
	}(whitespace))
	fmt.Println(func(X string) bool {
		upper_found := false
		for _, r := range X {
			if !unicode.IsUpper(r) {
				if !unicode.IsSpace(r) {
					return false
				}
			} else {
				upper_found = true
			}
		}
		return upper_found && len(X) != 0
	}(upper))
	fmt.Println(strings.Join([]string{lower, crazy, upper}, hearts))
	fmt.Println(strings.ToLower(crazy))
	fmt.Println(strings.TrimLeftFunc(s_hello_s, unicode.IsSpace) + "|")
	fmt.Println(strings.TrimLeft(lower, "h"))
	fmt.Println(strings.TrimPrefix(lower, "hello "))
	fmt.Println(strings.TrimSuffix(lower, " world"))
	fmt.Println(strings.ReplaceAll(lower, "world", "gophers"))
	fmt.Println(strings.Replace(upper, "O", "OOOOO", 1))
	fmt.Println(strings.LastIndex(upper, "O"))
	fmt.Println(func() int {
		if r := strings.LastIndex(upper[1:], "O"); r != -1 {
			return r + 1
		}
		return -1
	}())
	fmt.Println(func() int {
		if r := strings.LastIndex(upper[1:6], "O"); r != -1 {
			return r + 1
		}
		return -1
	}())
	fmt.Println(func(X string, sub string) int {
		if i := strings.LastIndex(X, sub); i != -1 {
			return i
		}
		panic(errors.New("ValueError: substring not found"))
	}(upper, "O"))
	fmt.Println(func(X string, sub string, start int) int {
		if i := func() int {
			if r := strings.LastIndex(X[start:], sub); r != -1 {
				return r + start
			}
			return -1
		}(); i != -1 {
			return i
		}
		panic(errors.New("ValueError: substring not found"))
	}(upper, "O", 1))
	fmt.Println(func(X string, sub string, start int, end int) int {
		if i := func() int {
			if r := strings.LastIndex(X[start:end], sub); r != -1 {
				return r + start
			}
			return -1
		}(); i != -1 {
			return i
		}
		panic(errors.New("ValueError: substring not found"))
	}(upper, "O", 1, 6))
	fmt.Println(strings.TrimRightFunc(s_hello_s, unicode.IsSpace) + "|")
	fmt.Println(strings.TrimRight(lower, "d"))
	fmt.Println(strings.Fields(lower))
	fmt.Println(strings.Split(upper, "L"))
	fmt.Println(strings.SplitN(upper, "L", 1))
	fmt.Println(func(s string) (lines []string) {
		sc := bufio.NewScanner(strings.NewReader(s))
		for sc.Scan() {
			lines = append(lines, sc.Text())
		}
		return
	}(multiline))
	fmt.Println(strings.HasPrefix(upper, "HELLO"))
	fmt.Println(strings.TrimSpace(s_hello_s) + "|")
	fmt.Println(strings.Trim(lol, "-"))
	fmt.Println(func(s string) string {
		ws := true
		var sb strings.Builder
		for _, r := range s {
			if unicode.IsSpace(r) {
				ws = true
				sb.WriteRune(r)
			} else if ws {
				ws = false
				sb.WriteRune(unicode.ToUpper(r))
			} else {
				sb.WriteRune(unicode.ToLower(r))
			}
		}
		return sb.String()
	}(crazy))
	fmt.Println(strings.ToUpper(crazy))
}

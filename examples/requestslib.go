package main

import (
	"fmt"
	"io/ioutil"
	"net/http"
)

func main() {
	resp, err := http.Get("http://tour.golang.org/welcome/1")
	if err != nil {
		panic(err)
	}
	defer resp.Body.Close()
	fmt.Println(func() string {
		body, err := ioutil.ReadAll(resp.Body)
		if err != nil {
			panic(err)
		}
		return string(body)
	}())
}

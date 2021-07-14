package main

import (
	"fmt"
	"time"
)

func main() {
	fmt.Println(float64(time.Now().UnixNano()) / 1000000000.0)
	fmt.Println(time.Now().UnixNano())
	fmt.Println(time.Now().Format("Mon Jan 02 15:04:05 2006"))
	fmt.Println(time.Unix(1000000000, 0).Format("Mon Jan 02 15:04:05 2006"))
}

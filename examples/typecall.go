package main

import (
	"fmt"
	"reflect"
)

type Custom1 struct{}

func NewCustom1() (self *Custom1) {
	self = new(Custom1)
	return
}

type Custom2 struct {
	x int
}

func NewCustom2(x int) (self *Custom2) {
	self = new(Custom2)
	self.x = x
	return
}

func main() {
	b := false
	i := 12
	f := 4.2
	s := "bla bla"
	sb := []byte("bla bla")
	s1 := map[int]struct{}{1: {}, 2: {}, 3: {}}
	s2 := map[string]struct{}{"a": {}, "b": {}, "c": {}}
	d1 := map[string]int{"hi": 1}
	d2 := map[string]string{"hi": "hi"}
	l1 := []int{1, 2, 3}
	l2 := []string{"a", "b", "c"}
	t1 := [3]int{1, 2, 3}
	t2 := [2]int{1, 2}
	c1 := NewCustom1()
	c2 := NewCustom2(1)
	c3 := NewCustom2(2)
	fx := func(x interface{}) {
		fmt.Println(x)
	}
	fxy := func(x interface{}, y interface{}) {
		fmt.Println(x, y)
	}
	fmt.Println("type(b) =", reflect.TypeOf(b))
	fmt.Println("type(i) =", reflect.TypeOf(i))
	fmt.Println("type(f) =", reflect.TypeOf(f))
	fmt.Println("type(s) =", reflect.TypeOf(s))
	fmt.Println("type(sb) =", reflect.TypeOf(sb))
	fmt.Println("type(d1) =", reflect.TypeOf(d1))
	fmt.Println("type(d2) =", reflect.TypeOf(d2))
	fmt.Println("type(l1) =", reflect.TypeOf(l1))
	fmt.Println("type(l2) =", reflect.TypeOf(l2))
	fmt.Println("type(t1) =", reflect.TypeOf(t1))
	fmt.Println("type(t2) =", reflect.TypeOf(t2))
	fmt.Println("type(c1) =", reflect.TypeOf(c1))
	fmt.Println("type(c2) =", reflect.TypeOf(c2))
	fmt.Println("type(s1) =", reflect.TypeOf(s1))
	fmt.Println("type(s2) =", reflect.TypeOf(s2))
	fmt.Println("type(c3) =", reflect.TypeOf(c3))
	fmt.Println("type(fx) =", reflect.TypeOf(fx))
	fmt.Println("type(fxy) =", reflect.TypeOf(fxy))
	fmt.Println("type(d1) == type(d2)?", reflect.TypeOf(d1).Kind() == reflect.TypeOf(d2).Kind())
	fmt.Println("type(l1) == type(l2)?", reflect.TypeOf(l1).Kind() == reflect.TypeOf(l2).Kind())
	fmt.Println("type(t1) == type(t2)?", reflect.TypeOf(t1).Kind() == reflect.TypeOf(t2).Kind())
	fmt.Println("type(l1) == type(t1)?", reflect.TypeOf(l1).Kind() == reflect.TypeOf(t1).Kind())
	fmt.Println("type(c1) == type(c2)?", reflect.TypeOf(c1) == reflect.TypeOf(c2))
	fmt.Println("type(c2) == type(c3)?", reflect.TypeOf(c2) == reflect.TypeOf(c3))
	fmt.Println("type(fx) == type(fxy)?", reflect.TypeOf(fx).Kind() == reflect.TypeOf(fxy).Kind())
	fmt.Println("type(s) == str?", reflect.TypeOf(s).Kind() == reflect.String)
	fmt.Println("type(sb) == bytes?", reflect.TypeOf(sb).Kind() == reflect.Slice)
	fmt.Println("type(i) == int?", reflect.TypeOf(i).Kind() == reflect.Int)
	fmt.Println("type(f) == float?", reflect.TypeOf(f).Kind() == reflect.Float64)
	fmt.Println("type(l1) == list?", reflect.TypeOf(l1).Kind() == reflect.Slice)
	fmt.Println("type(t1) == tuple?", reflect.TypeOf(t1).Kind() == reflect.Array)
	fmt.Println("type(s1) == type(s2)?", reflect.TypeOf(s1).Kind() == reflect.TypeOf(s2).Kind())
	fmt.Println("type(c1) == Custom1", reflect.TypeOf(c1) == reflect.TypeOf(new(Custom1)))
	fmt.Println("type(c2) == Custom2", reflect.TypeOf(c2) == reflect.TypeOf(new(Custom2)))
	fmt.Println("type(c2) == Custom1", reflect.TypeOf(c2) == reflect.TypeOf(new(Custom1)))
}

# pythagoras

Transpiles some Python into human-readable Golang.

## Goals

1. First, if you looked at a Go program and wrote a one-to-one implementation in Python, 
   I'd like that implementation to translate back into Go using this program.
2. After that is taken care of, I'd like to look at ways to convert normal Python programs into Go.

What do I mean by this? Well, if you're looking at go code and writing it back into Python, you're not
going to make a list that [1, "hello", Dog()] (probably). So to start, I'm going to write this assuming
a list in Python means we want a slice in Go with a single type. After all of that is working dandy,
maybe we can think about what do to if our list isn't so simple (probably involves wrapping each value in 
a struct).

## Differences in output program from input

There will be countless differences in the behavior of the output go vs the input python, but
we shall try to document the ones we observe (especially if we don't intend to fix them)

If it would require a lot of boilerplate code to imitate some Python behavior when the go program does
something different but fine for 99% of use cases, then I probably won't bother "fixing" it as it would
just result in generating uglier go code.

1. When you print out a float64 with a value of 1 in Golang, in Python it prints 1.0 but Golang just prints 1.

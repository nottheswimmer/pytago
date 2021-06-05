# pythagoras

Transpiles some Python to human-readable Golang.

## Differences in output program from input

There will be countless differences in the behavior of the output go vs the input python, but
we shall try to document the ones we observe (especially if we don't intend to fix them)

If it would require a lot of boilerplate code to imitate some Python behavior when the go program does
something different but fine for 99% of use cases, then I probably won't bother "fixing" it as it would
just result in generating uglier go code.

1. When you print out a float64 with a value of 1 in Golang, in Python it prints 1.0 but Golang just prints 1.

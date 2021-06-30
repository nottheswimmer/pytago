def bisection(function, a: float, b: float) -> float:
    start = a
    end = b
    if function(a) == 0:  # one of the a or b is a root for the function
        return a
    elif function(b) == 0:
        return b
    elif (
            function(a) * function(b) > 0
    ):  # if none of these are root and they are both positive or negative,
        # then this algorithm can't find the root
        raise ValueError("could not find root in given interval.")
    else:
        mid = start + (end - start) / 2.0
        while abs(start - mid) > 10 ** -7:  # until precisely equals to 10^-7
            if function(mid) == 0:
                return mid
            elif function(mid) * function(start) < 0:
                end = mid
            else:
                start = mid
            mid = start + (end - start) / 2.0
        return mid


def f(x: float):
    return x ** 3 - 2 * x - 5


def main():
    print(bisection(f, 1, 1000))

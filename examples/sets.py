def main():
    s = {1, 2, 3}
    # other = {3, 4}
    # another = {5, 6, 7}
    x = 1

    # len(s)
    print(len(s))

    # x in s
    print(x in s)

    # x not in s
    print(x not in s)

    # TODO:
    # # isdisjoint(other)
    # print(s.isdisjoint(other))
    #
    # # issubset(other)
    # # set <= other
    # # Test whether every element in the set is in other.
    # print(s.issubset(other))
    # print(s <= other)
    #
    # # set < other
    # # Test whether the set is a proper subset of other, that is, set <= other and set != other.
    # print(s < other)
    #
    # # issuperset(other)
    # # Test whether every element in other is in the set.
    # print(s >= other)
    #
    # # set > other
    # # Test whether the set is a proper superset of other, that is, set >= other and set != other.
    # print(s > other)
    #
    # # union(*others)
    # # set | other | ...
    # print(s.union(other))
    # print(s.union(other, another))
    # print(s | other)
    # print(s | other | another)
    #
    # # intersection(*others)
    # # set & other & ...
    # print(s.intersection(other))
    # print(s.intersection(other, another))
    # print(s & other)
    # print(s & other & another)
    #
    # # difference(*others)
    # # set - other - ...
    # # Return a new set with elements in the set that are not in the others.
    # print(s.difference(other))
    # print(s.difference(other, another))
    # print(s - other)
    # print(s - other - another)
    #
    # # symmetric_difference(other)
    # # set ^ other
    # # Return a new set with elements in either the set or other but not both.
    # print(s.symmetric_difference(other))
    # print(s ^ other)
    #
    # # copy()
    # # Return a shallow copy of the set.
    # print(s.copy())
    #
    # # The following table lists operations available for set that do not apply to
    # # immutable instances of frozenset:
    #
    # # update(*others)
    # # set |= other | ...
    # # Update the set, adding elements from all others.
    # s.update(other)
    # print(s)
    # s.update(other, another)
    # print(s)
    # another |= other
    # print(another)
    # another |= other | s
    # print(another)
    #
    #
    # # intersection_update(*others)
    # # set &= other & ...
    # # Update the set, keeping only elements found in it and all others.
    # s.intersection_update(other)
    # print(s)
    # s.intersection_update(other, another)
    # print(s)
    # another &= other
    # print(another)
    # another &= other & s
    # print(another)
    #
    # # difference_update(*others)
    # # set -= other | ...
    # # Update the set, removing elements found in others.
    # s.difference_update(other)
    # print(s)
    # s.difference_update(other, another)
    # print(s)
    # another -= other
    # print(another)
    # another -= other | s
    # print(another)
    #
    # # symmetric_difference_update(other)
    # # set ^= other
    # # Update the set, keeping only elements found in either set, but not in both.
    # s.symmetric_difference_update(other)
    # print(s)
    # another ^= other
    # print(another)
    #
    # # add(elem)
    # # Add element elem to the set.
    # s.add(x)
    # print(s)
    #
    # # remove(elem)
    # # Remove element elem from the set. Raises KeyError if elem is not contained in the set.
    # s.remove(x)
    # print(s)
    #
    # # discard(elem)
    # # Remove element elem from the set if it is present.
    # s.discard(x)
    # print(s)
    #
    # # pop()
    # # Remove and return an arbitrary element from the set. Raises KeyError if the set is empty.
    # print(s.pop())
    #
    # # clear()
    # # Remove all elements from the set.
    # s.clear()
    # print(s)


if __name__ == '__main__':
    main()

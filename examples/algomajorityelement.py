def majorityElement(nums: list[int]) -> int:
    element, cnt = 0, 0

    for e in nums:
        if element == e:
            cnt += 1
        elif cnt == 0:
            element, cnt = e, 1
        else:
            cnt -= 1

    return element

def main():
    print(majorityElement([3,2,3]))  # 3
    print(majorityElement([2,2,1,1,1,2,2]))  # 2

if __name__ == '__main__':
    main()

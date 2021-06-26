A = [1, 2, 3]

for i, x in enumerate(A):
    A[i] += x

B = A[0]
C = A[0]
D: int = 3

while C < A[2]:
    C += 1

if C == A[2]:
    print('True')


def main():
    print("Main started")
    print(A)
    print(B)
    print(C)
    print(D)


if __name__ == '__main__':
    main()

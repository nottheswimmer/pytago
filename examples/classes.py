class Welcome:
    greeting: str
    instructions: list[str]

    def __init__(self, greeting: str, instructions: list[str]) -> None:
        self.greeting = greeting
        self.instructions = instructions

    def greet(self):
        print(self.greeting)
        for instruction in self.instructions:
            print(instruction)


def main():
    welcome = Welcome("Hello World", [
        "This is a class!",
        "Support will be limited at first.",
        "Still, I hope you'll find them useful."
    ])
    welcome.greet()


if __name__ == '__main__':
    main()

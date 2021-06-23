def main():
    lower = "hello world"
    crazy = "HeLLo WoRlD"
    upper = "HELLO WORLD"
    lol = "---LOL---"
    hearts = "🧡💛💚💙💜"
    arabic_indic_digit = "٠"
    whitespace = " \v\f\t\r\n"
    s_hello_s = whitespace + lower + whitespace
    multiline = lower + "\n" + crazy + "\r\n" + upper + "\n"

    print(crazy.capitalize())
    print(lower.endswith("world"))
    print(lower.find(" "))
    print(lower.find(" ", 2))
    print(upper.find(" ", 7, 8))
    print(lower.index(" "))
    print(lower.index(" ", 2))
    print(upper.index(" ", 2, 8))
    print(lower.isalnum())
    print(hearts.isascii())
    print(arabic_indic_digit.isdecimal())
    print(arabic_indic_digit.isdigit())
    print(lower.islower())
    print(arabic_indic_digit.isnumeric())
    print(hearts.isprintable())
    print(whitespace.isspace())
    print(upper.isupper())
    print(hearts.join([lower, crazy, upper]))
    print(crazy.lower())
    print(s_hello_s.lstrip() + "|")
    print(lower.lstrip("h"))
    print(lower.removeprefix("hello "))
    print(lower.removesuffix(" world"))
    print(lower.replace("world", "gophers"))
    print(upper.replace("O", "OOOOO", 1))
    print(upper.rfind("O"))
    print(upper.rfind("O", 1))
    print(upper.rfind("O", 1, 6))
    print(upper.rindex("O"))
    print(upper.rindex("O", 1))
    print(upper.rindex("O", 1, 6))
    print(s_hello_s.rstrip() + "|")
    print(lower.rstrip("d"))
    print(lower.split())
    print(upper.split("L"))
    print(upper.split("L", 1))
    print(multiline.splitlines())
    print(upper.startswith("HELLO"))
    print(s_hello_s.strip() + "|")
    print(lol.strip("-"))
    print(crazy.title())
    print(crazy.upper())


if __name__ == '__main__':
    main()

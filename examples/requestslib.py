import requests


def main():
    resp = requests.get("http://tour.golang.org/welcome/1")
    print(resp.text)

if __name__ == '__main__':
    main()

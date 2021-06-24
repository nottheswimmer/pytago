from argparse import ArgumentParser

from pytago import python_to_go

parser = ArgumentParser(prog='Pytago')
parser.add_argument("-o", "--out", dest="outfile", help="write go code to OUTFILE", metavar="OUTFILE")
parser.add_argument('infile', help='read python code from INFILE', metavar="INFILE")


def main():
    args = parser.parse_args()
    if args.infile:
        with open(args.infile, "r") as f:
            go = python_to_go(f.read(), debug=False)
            if args.outfile:
                with open(args.outfile, "w", encoding='utf8') as f:
                    f.write(go)
            else:
                print(go)


if __name__ == '__main__':
    main()

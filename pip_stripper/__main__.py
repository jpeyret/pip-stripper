import sys

from pip_stripper._pip_stripper import Main


def main(args=None):
    """The main routine."""
    # if args is None:
    #     args = sys.argv[1:]

    print("This is the main routine.")
    print("It should do something interesting.")

    # Do argument parsing here (eg. with argparse) and anything else
    # you want your project to do.

    print(":sys.argv:%s:" % (sys.argv))

    if args is None:
        args = sys.argv

    parser = Main.getOptParser()
    options = parser.parse_args(args)
    mgr = Main(options)
    mgr.process()


if __name__ == "__main__":
    main()

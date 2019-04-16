import sys

from pip_stripper._pip_stripper import Main


def main(args=None):
    """The main routine."""

    if args is None:
        args = sys.argv[1:]

    parser = Main.getOptParser()
    options = parser.parse_args(args)

    mgr = Main(options)
    mgr.process()


if __name__ == "__main__":
    main()

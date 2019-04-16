import sys

from pip_stripper._pip_stripper import Main


def main(args=None):
    """The main routine."""

    if args is None:
        args = sys.argv[:1]

    parser = Main.getOptParser()
    print("args:%s" % (args))
    options = parser.parse_args(args)
    print("options:%s" % (options))

    mgr = Main(options)
    print("mgr:%s" % (mgr))
    mgr.process()


if __name__ == "__main__":
    main()

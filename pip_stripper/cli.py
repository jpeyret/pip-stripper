# -*- coding: utf-8 -*-

"""Console script for pip_stripper."""
import sys
import click

# from pip_stripper import _baseutils
import pip_stripper._baseutils

@click.command()
def main(args=None):
    """Console script for pip_stripper."""
    click.echo("Replace this message by putting your code into "
               "pip_stripper.cli.main")
    click.echo("See click documentation at http://click.pocoo.org/")
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover

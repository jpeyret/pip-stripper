import re
import pdb

from yaml import safe_load as yload, dump


from pip_stripper._baseutils import ppp, cpdb


class Commenter(object):
    """
    inject 1-line comments at precise locations in existing yaml files
    """

    @classmethod
    def markup(cls, key):
        return "comment_lookup_%s" % (key)

    patre = re.compile("""\s*[a-z_A-Z0-9]+\:\scomment_lookup_(?P<lookup>.+)$""")

    def __init__(self, fnp_lookup):
        self.fnp_lookup = fnp_lookup
        with open(fnp_lookup) as fi:
            self.comments = yload(fi)

    def lookup(self, key):
        return self.comments.get(key, "")

    def comment(self, fnp_in, fnp_out, mode="w"):
        try:
            with open(fnp_in) as fi, open(fnp_out, mode) as fo:
                for line in fi.readlines():
                    # pdb.set_trace()

                    hit = self.patre.search(line)
                    if hit:

                        indent = " " * (len(line) - len(line.lstrip()))
                        key = hit.groups()[0]
                        comment = self.lookup(key)
                        fo.write("\n%s#%s\n" % (indent, comment))
                    else:
                        fo.write(line)
        except (Exception,) as e:
            if cpdb():
                pdb.set_trace()
            raise

    __call_ = comment

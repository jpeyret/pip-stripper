
def cpdb(**kwds):
    cpdb.enabled = False


class Matcher(object):

    def __init__(self):

        self.pip = Side("pip", _variations_pip)
        self.imp = Side("imp", _variations_imp)

        self.di_pip_imp = dict()

    def do_match(self):
        try:
        
            self.matches = self.pip.s_alias & self.imp.s_alias

            for match in self.matches:
                pip = self.pip.di_alias[match]
                imp = self.imp.di_alias[match]

                self.di_pip_imp[pip] = imp

        except (Exception,) as e:
            if cpdb(): pdb.set_trace()
            raise

class Side(object):

    def __repr__(self):
        return self.subject

    def __init__(self, subject, li_varfunc):
        self.subject = subject
        self.di_name = {}
        self.li_varfunc = li_varfunc
        self.s_alias = set()

        self.di_alias = {}

        self.di_duplicates = {}

    def get_aliases(self, name):
        try:

            def alias(name, func):
                try:
                    return func(name)
                except (Exception,) as e:
                    return None

            name = name.lower()
            res = set([i for i in [alias(name, f) for f in self.li_varfunc] if i])
            return res

        except (Exception,) as e:
            if cpdb(): pdb.set_trace()
            raise        

    def feed(self, name):
        try:
            entry = self.di_name[name] = name

            aliases = self.get_aliases(name)

            #check for duplicates:
            dup = self.s_alias & aliases
            if dup:
                raise NotImplementedError("%s. alias duplicates:%s " % (self, dup))

            self.s_alias |= aliases

            self.di_alias.update(**{k:entry for k in aliases})

        except (Exception,) as e:
            if cpdb(): pdb.set_trace()
            raise


_variations = [
    str,
]

_variations_pip = _variations + [
    lambda x: x.split("-")[1],
]

_variations_imp = _variations + [
    lambda x: x.split("_")[1],
]

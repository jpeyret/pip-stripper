
class Dummy(dict):
    def __init__(self, **kwds):
        self.__dict__.update(**kwds)



class Matcher(object):

    def __init__(self):

        self.pip = Side("pip", _variations_pip)
        self.imp = Side("imp", _variations_imp)

class Side(object):
    def __init__(self, subject, li_varfunc):
        self.subject = subject
        self.di_name = {}
        self.li_varfunc = li_varfunc
        self.s_alias = set()

    def feed(self, name):
        self.di_name[name] = Name(self, name)

_variations = [
    str,
]


_variations_pip = _variations + [
    lambda x: x.split("-")[1],
]

_variations_imp = _variations + [
    lambda x: x.split("_")[1],
]


class Name(object):

    def get_aliases(self, name):
        try:

            def alias(self, name, func):
                try:
                    return func(name)
                except (Exception,) as e:
                    return None

            name = name.lower()
            res = set([i for i in [alias(name, f) for f in self.owner.li_varfunc] if i])
            return res

        except (Exception,) as e:
            if cpdb(): pdb.set_trace()
            raise

    def __init__(self, owner, name):
        self.name = name
        self.owner = owner
        li_func 

        self.aliases = [Alias(self, alias) for alias in self.variations(name)]




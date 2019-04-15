![https://pypi.python.org/pypi/pip-stripper](https://img.shields.io/pypi/v/pip-stripper.svg)  ![https://travis-ci.org/jpeyret/pip-stripper](https://img.shields.io/travis/jpeyret/pip-stripper.svg) [![Coverage Status](https://coveralls.io/repos/github/jpeyret/pip-stripper/badge.svg?branch=master)](https://coveralls.io/github/jpeyret/pip-stripper?branch=master)

# TLDR:  requirements without *unnecessary* `pip` packages.



~~~
For the purpose of this exercise, an unnecessary pip package is any package that is not being 
imported by YOUR own Python code.  
Unless you've provided a configuration override stating that you want it.
~~~

For example, let's say that you have installed `black 18.9b0`.  A linter and autoformatter, while very useful in development has no need to be on a server:

`pip-stripper` won't find `import black` anywhere, so it will not put it in `requirements`



# How it works

````
usage: _pip_stripper.py [-h] [--config CONFIG] [--scan] [--build] [--init]
                        [--workdir WORKDIR] [--verbose]

optional arguments:
  -h, --help         show this help message and exit
  --config CONFIG    config - will look for pip-stripper.yaml in --workdir,
                     current directory
  --scan             scan scan python files and classify packages [True]
  --build            build [False]
  --init             init initialize the config file if it doesn't exist
  --workdir WORKDIR  workdir [defaults to config's value or current directory]
  --verbose          verbose [False]
````

## Three phases, `initialization`, `scan` and `build`.


### Initialization

The first option `--init` will create **pip-stripper.yaml**, the configuration file for pip-stripper.

**This is the only file you should edit manually!!!**


### Scan

The second option, `--scan`, will scan your Python source files in `--workdir` and use it to create **pip-stripper.scan.yaml**.  

This is the file that contains instructions for the build phase.  

**Don't edit pip-stripper.scan.yaml!**  

Instead:
 - adjust the configuration in **pip-stripper.yaml**
 - re-run the scan

`--scan` also creates 2 work files, `tmp.pip-stripper.freeze.rpt` and  `tmp.pip-stripper.imports.rpt`, tracking pip packages and its best guesses at python imports, respectively.


### Build.

`--build` will take what it found in **pip-stripper.scan.yaml** and use it to populate 
`requirements.prod.txt` and `requirements.dev.txt`.

If you don't agree with what's in those requirements files, you may need to edit **pip-stripper.yaml**.

## Editing `pip-stripper.yaml`

This allows you to specify:

- `pip` vs `import` aliases
- specify which packages are just *workstation*-level and shouldn't go into requirements.
- hardcode packages that need to go into either.
- Associating your source directories to either `prod` or `dev`.

### Aliases

You may have to enter pip to python import alias names manually (alias matching is something that needs work). 

````
hardcoded_aliases:
  PyYAML: yaml
````


### Hardcoding package to requirement mapping:

Because `psycopg2` is typically never really imported in a Django or SQLAlchemy context, but rather derived from the configuration, you need to specify it yourself as below.  Same thing with `django-redis-cache` which is configured in django's `settings.py` as package path rather than an import.  

````
ClassifierPip:

  #the following are used to "hardcode" package names to given buckets.
  buckets:
    prod:
      - psycopg2
      - django-redis-cache

    tests:
      - nose
      - pytest

    workstation:
      # that's a workstation only package, so it's held back
      - black
````

#### Associating Python directories to requirements:

This is a typical regex-based configuration telling which *buckets* the directories count as:

`prod` is the default outcome.  First match wins, and `tests` is the only one needed.

````
ClassifierImport:
  regex_dirs:
    workstation: []
    dev: []
    tests:
      - "/tests/"
    prod: []

  default_bucket: "prod"

````

### Walkthrough:

#### case 1: hardcoding

Given a `pip freeze` line like 

````
psycopg2==2.7.7
````


First, it looks for a matching entry in `ClassifierPip:buckets` in **pip-stripper.yaml**, (basically a hardcoded decision by the user of where to put it).
        
````
ClassifierPip:
  buckets:
    workstation:
      - black
    prod:
      - psycopg2
````

This will result in `psycopg2==2.7.7` going into **requirements.prod.txt** (when needed, requirements lines are always copied from the `pip freeze` output).

#### case 2: import classification.

`grep`-ing the Python code found this line:

````
./tests/helper_pyquery.py:57:    from pyquery import PyQuery
````

Each file path is run against the regex specified by `ClassifierImport:regex_dirs`, so pyquery ends up in the `tests` bucket.

````
ClassifierImport:
  regex_dirs:
    tests:
      - "/tests/"
    prod: []
  default_bucket: "prod"
````

finally, the `--build` pass looks at where buckets get mapped:

````
Builder:
  req_mapper:
    dev:
      buckets:
        - dev
        - tests   
    prod:
      buckets:
        - prod
````

which puts `pyquery` in `requirements.dev.txt`.

### case 3 multiple imports

````
./tests/helper_pyquery.py:57:    from pyquery import PyQuery
./myserver/foobar.py:22:    from pyquery import PyQuery
````

As before, `pyquery` is put in `tests` and `prod` buckets. But also in `prod` as  `myserver` did not match any `ClassifierImport:regex_dirs`, meaning that `default_bucket: "prod"` was used.

enter *bucket precedence*

````
ClassifierPip:
  bucket_precedence:
    - prod
    - tests
    - dev
    - workstation
````

`prod` beats `tests` so `pyquery` ends up only in `prod` bucket.

### case 4.  no import match was found and nothing was hardcoded.

`Babel==2.6.0`

will get left out of requirements.  Which is not to say that it won't end up `pip installed` on your server if it is a dependency of some other package ([`pipdeptree`](https://pypi.org/project/pipdeptree/) can help you there).

````
Babel==2.6.0
  - pytz [required: >=0a, installed: 2018.9]

````

##Build Phase - the result of the `--scan` phase gets put into **pip-stripper.scan.yaml**:

Notice our friend `black`?  We've explicitly classified it as *workstation*, so the scan didn't label it as *unknown*.

````
pips:
  buckets:
    dev:
    	....
    tests:
    - pyquery
    prod:
    - psycopg2
    unknown:
    - Babel
    workstation:
    - black        
````

Look at the end for the `warnings:` section.  In this case, `repr` was used with Python 2.7 but isn't necessary with Python 3, so I won't worry about it.  A typical reason for a missing import is that automatic aliasing to link the pip name and import name didn't work. 

````
warnings:
- missing import:repr
````



### And that's it.  The outcome?

my raw pip freeze weighs in at 158 packages:

````
$ wc -l requirements.freeze_raw.txt
158 requirements.freeze_raw.txt
````

my stripped down requirements ended up with 24 packages total:

````
$ wc -l requirements*txt | egrep 'prod|dev'
6 requirements.dev.txt
18 requirements.prod.txt
````

On my test environment, `pip install -r requirements.prod.txt -r requirements.dev.txt` got me 48 packages, after dependencies were pulled in.

````
$ pip freeze | wc -l
48
````

# This is all very nice, but hopefully you have sufficient tests to allow you to be confident you didn't miss anything!

The way you can test is to create a new virtualenv, pip install both requirements files and then run your tests.

### WARNING:  be cautious in hardcoding package associations in dev/tests buckets rather than prod.  Your tests could run to success, but production would still fail.

These are pretty conservative as nose and pytest are really only testing tools.

````
ClassifierPip:
  buckets:
    tests:
      - nose
      - nose2
      - pytest
````
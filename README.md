FOIA tracker prototype, based on birddog app from News Hack Day

[![Build Status](https://magnum.travis-ci.com/cirlabs/foiamachine.png?token=bGVGgB8ujqt3coFYcr4e&branch=master)](https://magnum.travis-ci.com/cirlabs/foiamachine)

Requirements
------------

* Python
* git
* virtualenv
* Mercurial
* libmemcached-dev
* MySQL

for Ubuntu, some help:
* sudo apt-get install libmemcached-dev
* sudo apt-get install mercurial meld
* sudo apt-get install python-dev libmysqlclient-dev




Getting started
---------------

Create a new virtual environment and jump in.

```bash
$ virtualenv foiamachine
$ cd foiamachine
$ . bin/activate
```

Clone the repository.

```bash
$ git clone git@github.com:cirlabs/foiamachine.git repo
```

Jump in and install the Python requirements.

```bash
$ cd repo
$ pip install -r requirements.txt
```

Create a MySQL database and create our base tables.

```bash
$ echo "create database foiamachine" | mysql -u <your_db_user_here> -p
$ python foiamachine/manage.py syncdb
$ python foiamachine/manage.py migrate
```

Load default data.

```bash
$ python foiamachine/manage.py load_all_data
```

Fire up the runserver and take a look at [localhost:8000](http://localhost:8000)


```bash
$ fab rs
```

#SASS Setup

```
gem install sass
gem install compass
gem install zen-grids
gem install sassy-buttons
compass create . --bare --sass-dir "foiamachine/assets/sass" --css-dir "foiamachine/assets/css" --javascripts-dir "foiamachine/assets/js" --images-dir "foiamachine/assets/img" --force
compass install sassy-buttons
```

#LICENSE

The MIT License (MIT)

Copyright (c) 2014 Shane Shifflett 

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

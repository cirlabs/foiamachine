# CIR news applications fabfile for Heroku
# Modified from work by the Chicago Tribune's News Applications team
# We encourage you to copy this floppy (http://www.youtube.com/watch?v=up863eQKGUI)

import os
from datetime import datetime
from fabric.api import *
from os import environ


read_env = lambda e, d: environ[e] if environ.has_key(e) else d

BASE_DIR = os.path.dirname(os.path.realpath(__file__))

"""
Base configuration
"""
env.project_name = 'foiamachine'
env.database_password = 'birddog'
env.site_media_prefix = "static"
env.admin_media_prefix = "admin_media"
env.dbserver_path = '/home/projects' % env
env.localpath = BASE_DIR
env.python = 'python2.7'

"""
Environments
"""


def production():
    """
    Work on production environment
    """
    env.settings = 'production'
    env.hosts = ['foiamachine.org']
    env.user = 'foiamachine'
    env.s3_bucket = 's3.amazonaws.com/foi-staging-media/'

def staging():
    """
    Work on staging environment
    """
    env.settings = 'staging'
    env.hosts = ['staging-foiamachine.herokuapp.com']
    env.user = 'foiamachine'
    env.s3_bucket = 's3.amazonaws.com/foia-prod-media/'
"""
Running OSX?
"""


def install_homebrew():
    """
    Installs homebrew -- the sane OSX package manager.
    """
    local('/usr/bin/ruby -e "$(curl -fsSL https://raw.github.com/gist/323731)"')


def setup_osx():
    """
    OSX is going to throw a fit if you try to bootstrap a virtualenv from the
    requirements file without doing the following. Requires homebrew. You can
    either run install_homebrew above or follow the instructions here:
    https://github.com/mxcl/homebrew/wiki/installation
    """
    local('brew install libmemcached')
    local('brew install libevent')

"""
Local bootstrap
"""


def bootstrap():
    """
    Local development bootstrap: you should only run this once.
    """
    # Install requirements
    local("pip install -r ./requirements.txt")

    # Create database
    create_database(local)
    local("python ./%(project_name)s/manage.py syncdb --noinput" % env)

    # Set virtualenv vars for local dev
    # local('echo "export PROJECT_NAME=\"%(project_name)s\"" >> $WORKON_HOME/%(project_name)s/bin/postactivate' % env)
    # local('echo "export DJANGO_SETTINGS_MODULE=\"%(project_name)s.settings\"" >> $WORKON_HOME/%(project_name)s/bin/postactivate' % env)
    # local('echo "export PYTHONPATH=%(localpath)s:%(localpath)s/%(project_name)s" >> $WORKON_HOME/%(project_name)s/bin/postactivate' % env)
    # local('echo "export PATH=$PATH:%s" >> $WORKON_HOME/%s/bin/postactivate' % (BASE_DIR, env.project_name))
    # local('echo -e "*.pyc\ndata\\n%(project_name)s/gzip" > .gitignore' % env)

"""
Heroku
"""


def setup_heroku():
    """
    Performs initial setup on heroku.
    """
    local("cd %(localpath)s" % env)
    local("git init")
    local("git add .")
    local("git commit -m 'Initial commit'")
    local("heroku create -s cedar --buildpack http://github.com/cirlabs/heroku-buildpack-geodjango.git" % env)


def deploy_to_heroku():
    local("pip freeze > requirements.txt")
    local("git add .")
    prompt("Type your commit message here:", key='commitmessage')
    local("git commit -m '%(commitmessage)s';" % env)
    local("git push heroku master")


def heroku_shell():
    local("heroku run python %(project_name)s/manage.py shell --settings=%(project_name)s.settings.production")


def heroku_clear_cache():
    local("heroku run python %(project_name)s/manage.py clearcache --settings=%(project_name)s.settings.production" % env)

"""
Static media
"""


def gzip_assets():
    """
    GZips every file in the assets directory and places the new file
    in the gzip directory with the same filename.
    """
    local('cd %s; python ./gzip_assets.py' % BASE_DIR)


def deploy_to_s3():
    """
    Deploy the latest project site media to S3.
    """
    env.gzip_path = '%(localpath)s/%(project_name)s/gzip/static/' % env
    local(('s3cmd -P --add-header=Content-encoding:gzip --guess-mime-type --rexclude-from=%(localpath)s/s3exclude sync %(gzip_path)s s3://%(s3_bucket)s/%(project_name)s/%(site_media_prefix)s/') % env)


def deploy_static():
    print env
    local("python ./%(project_name)s/manage.py collectstatic" % env)
    #gzip_assets()
    #deploy_to_s3()

def compile_sass():
    local('compass create . --bare --sass-dir "foiamachine/assets/sass" --css-dir "foiamachine/assets/css" --javascripts-dir "foiamachine/assets/js" --images-dir "foiamachine/assets/img" --force')

def django_compress():
    local("python ./%(project_name)s/manage.py compress" % env)

def prepare_css_js():
    compile_sass()
    django_compress()

"""
Deaths, destroyers of worlds
"""


def shiva_the_destroyer():
    """
    Remove all directories, databases, etc. associated with the application.
    """
    with settings(warn_only=True):
        prompt("What's the name of your app on Heroku? (ex. strong-sword-3895):", key='appname')
        local('heroku apps:destroy --app %(appname)s' % env)
        destroy_database()
        run('s3cmd del --recursive s3://%(s3_bucket)s/%(project_name)s' % env)


def shiva_local():
    """
    Undo any local setup.  This will *destroy* your local database, so use with caution.
    """
    destroy_database(local)

"""
3 ... 2 ... 1 ... blastoff
"""


def blastoff():
    deploy_data()
    deploy_static()
    deploy_to_heroku()

#
# Misc. tricks
#

def rmpyc():
    """
    Erases pyc files from current directory.

    Example usage:

    $ fab rmpyc

    """
    print("Removing .pyc files")
    with hide('everything'):
        local("find . -name '*.pyc' -print0|xargs -0 rm", capture=False)


def rs(port=8000):
    """
    Fire up the Django test server, after cleaning out any .pyc files.

    Example usage:
    $ fab rs
    $ fab rs:port=9000
    """
    with settings(warn_only=True):
        rmpyc()
    local("python ./%s/manage.py runserver 0.0.0.0:%s" % (
            env.project_name,
            port
        ),
        capture=False)


def sh():
    """
    Fire up the Django shell, after cleaning out any .pyc files.

    Example usage:
    $ fab sh
    """
    rmpyc()
    local("python ./%s/manage.py shell" % env.project_name, capture=False)

def backup():
    host = read_env("DBHOST", "") 
    db = read_env("DBNAME", "")
    user = read_env("DBUSER", "")
    port = 3306
    print user
    date = datetime.now().strftime("%m%d%Y")
    cmd = "/usr/local/mysql/bin/mysqldump -h%s  -u%s -P%s %s -p > %sdump.sql" % (host, user, port, db, date)
    local(cmd)

def restore_local(filename):
    try:
        cmd = "/usr/local/mysql/bin/mysql -uroot -e 'drop database foiamachine;'"
        print cmd
        local(cmd)
    except:
        pass
    try:
        cmd = "/usr/local/mysql/bin/mysql -uroot -e 'create database foiamachine;'"
        print cmd
        local(cmd)
    except:
        pass
    cmd = "/usr/local/mysql/bin/mysql -uroot foiamachine < %s" % filename
    local(cmd)

"""This module is the main function.
"""
#
#   Author: zhongpei
#
#   Date: 06/12/2017
#

from ConfigParser import ConfigParser
import codecs
import os
import subprocess
import multiprocessing
import datetime
from leetcode import LeetcodeCrawler
from formatter import code_formatter, description_formatter, path_formatter


def read_from_config():
    """Read from config.cfg.

    Returns:
        a dictionary containing the username, password,
        languages, problems and github reops read from
        config.cfg.
    """
    config = ConfigParser()
    config.read('config.cfg')
    secs = config.sections()
    if 'leetcode' not in secs:
        raise Exception('Add [leetcode] in your config file')

    opts = config.options('leetcode')
    if 'username' not in opts or 'password' not in opts:
        raise Exception('Please add your username and password in config file')
    username = config.get('leetcode', 'username')
    password = config.get('leetcode', 'password')
    if not username or not password:
        raise Exception('Please set your username and password in config file')

    if 'languages' not in opts:
        raise Exception('Please add languages in config file')
    langs = config.get('leetcode', 'languages')
    # if no languages, set python as default
    languages = langs.split(',') if langs else ['python']

    if 'problems' not in opts:
        raise Exception('Please add problems in config file')
    problems = []
    probs = config.get('leetcode', 'problems')
    problems = [int(p) for p in probs.split(',')] if probs else []

    opts = config.options('github')
    if 'github' not in secs:
        raise Exception('Add [github] in your config file')
    if 'repo' not in opts:
        raise Exception('Please add repo in config file')
    repo = config.get('github', 'repo')
    if not repo:
        raise Exception('Please add repo in config file')

    return dict(username=username, password=password, languages=languages,
                problems=problems, repo=repo)


def crawl_with_multiprocesses(message):
    """Crawl problems and write them in a file.

    Args:
        a tuple contains config info, problems and a LeetcodeCrawler instance.
    """
    cf, lcc, p = message
    lcc.get_submissions(p)
    for lang in cf['languages']:
        tdc = lcc.get_title_description_code(lang)
        if not tdc:
            continue
        print 'Downloading problem %d' % (p)
        title, description, code = tdc
        fp, fn = path_formatter(p, title, lang)
        fd = description_formatter(description, lang)
        fc = code_formatter(code)
        path_name = cf['repo'] + fp
        if not os.path.isdir(path_name):
            os.makedirs(path_name)
        with codecs.open(path_name + fn, 'w', 'utf-8') as f:
            print 'Writing problem %d' % (p)
            f.write(fd + fc)


def git_commit(repo):
    """Commit and push to github.
    """
    time = datetime.datetime.now()
    message = time.strftime('%m/%d/%y')

    git_add = 'git add .'
    git_commit = "git commit -m '%s'" % (message)
    git_push = 'git push -u origin master'

    # change to github repo directory, and exectue git command.
    prev_dir = os.getcwd()
    os.chdir(repo)
    subprocess.call(git_add, shell=True)
    subprocess.call(git_commit, shell=True)
    subprocess.call(git_push, shell=True)
    os.chdir(prev_dir)


def crawl_and_commit():
    """Crawl problems and write them in a file.
    """
    print 'Reading configurations...'
    cf = read_from_config()

    lcc = LeetcodeCrawler()

    print 'Checking cookies...'
    if not lcc.is_login():
        lcc.login(cf['username'], cf['password'])

    print 'Starting to crawl...'
    lcc.get_problems_dict()    # get the problem list
    # if problem is set to '', get all problem ids.
    probs = cf['problems'] if cf['problems'] else lcc.problems.keys()

    # start multiprocesses
    cpus = multiprocessing.cpu_count()  # number of processes
    pool = multiprocessing.Pool(processes=cpus)
    message = [(cf, lcc, prob) for prob in probs]
    pool.map(crawl_with_multiprocesses, message)
    pool.close()
    pool.join()
    print 'Finished Downloading and Writing!'

    print 'Committing to github...'
    git_commit(cf['repo'])

    print 'Done!'


if __name__ == '__main__':
    crawl_and_commit()

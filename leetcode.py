"""This module contains the LeetcodeCrawler class.
All crawler functions are in this module.
"""

#
#   Author: zhongpei
#
#   Date: 06/12/2017
#

import re
import json
import os
from selenium import webdriver
import requests
from lxml import etree


class LeetcodeCrawler(object):
    """Leetcode crawler focus on crawling problems,
    submissions, and code from Leetcode.
    """
    BASE_URL = 'https://leetcode.com'
    HEADERS = {
        'User-Agent': 'Mozilla/5.0'
    }
    COOKIE_FILE = 'cookies.json'
    PROBLEMS_LIST = 'problems.json'

    def __init__(self):
        self.__session = requests.Session()
        self.__problems = None
        self.__submissions = None

    @property
    def problems(self):
        """return problems"""
        return self.__problems

    @property
    def submissions(self):
        """return submissions"""
        return self.__submissions

    def login(self, username, password):
        """Login in to the Leetcode ans save the cookie."""
        login_url = self.BASE_URL + '/accounts/login/'
        if not username or not password:
            raise Exception('Please add your leetcode account in config file')

        driver = webdriver.PhantomJS()
        driver.get(login_url)

        user_input = driver.find_element_by_xpath("//input[@id='id_login']")
        pwd_input = driver.find_element_by_xpath("//input[@id='id_password']")
        submit = driver.find_element_by_xpath("//button[@type='submit']")
        user_input.send_keys(username)
        pwd_input.send_keys(password)
        submit.click()

        cookies = {str(cookie['name']): str(cookie['value'])
                   for cookie in driver.get_cookies()}
        with open(self.COOKIE_FILE, 'w') as cookie_file:
            json.dump(cookies, cookie_file)
        self.__session.headers.update(self.HEADERS)
        self.__session.cookies.update(cookies)
        driver.close()

    def is_login(self):
        """Check if the cookie is valid.

        Returns:
            True if cookie is valid, otherwise False.
        """
        if not os.path.isfile(self.COOKIE_FILE):
            return False
        with open(self.COOKIE_FILE, 'r') as cookie_file:
            cookies = json.load(cookie_file)
        self.__session.cookies.update(cookies)
        self.__session.headers.update(self.HEADERS)
        rep = self.__session.get(self.BASE_URL + '/api/problems/algorithms')
        if rep.status_code == 200:
            data = rep.json()
            return 'user_name' in data and data['user_name'] != ''
        return False

    def get_title_description_code(self, lang):
        """Get the code from submissions with minimal runtime. If several
        codes have the same shortest runtime, get the most recent one.
        Get problem description.
        Get the problem title.

        Args:
            lang: a string representing the programming languages.

        Returns:
            A string tuple representing title, description and code.
            None if no code is found.
        """
        if not self.__submissions:
            return None

        # get the submission of the given language
        candidates = [sub for sub in self.__submissions if sub['lang'] == lang]
        if not candidates:
            return None

        # get the submission with the minimal runtime
        candidate = min(candidates, key=lambda x: x['runtime'])

        rep = self.__session.get(self.BASE_URL + candidate['url'])

        # get description and title through xpath
        html = etree.HTML(rep.text)
        description = html.xpath("//meta[@name='description']/@content")[0]
        title = html.xpath("//meta[@property='og:title']/@content")[0]

        # get the code through regular expression
        pattern = re.compile('submissionCode: \'(?P<code>.*)\',')
        match = re.search(pattern, rep.text)
        code = match.group('code')

        return title, description, code

    def get_submissions(self, problem_id):
        """Get all accepted submissions of the given problem.

        Args:
            problem_id: an integer representing the id of the problem.
        """
        limit = 9999   # set it to a large number to get all submissions

        if not self.__problems:
            raise Exception('Get problem lists before getting submissions.')

        if problem_id not in self.problems:
            raise Exception('Wrong Problem Id %d' % (problem_id))

        problem = self.problems[problem_id]
        subs_url = ('%s/api/submissions/%s/?offset=0&limit=%d'
                    % (self.BASE_URL, problem['url'], limit))
        rep = self.__session.get(subs_url)
        data = rep.json()
        subs = data['submissions_dump']
        self.__submissions = [{
            'url': sub['url'],
            # convert string to int, for example: '3 ms' --> 3.
            'runtime': int(sub['runtime'].split(' ')[0]),
            'lang': sub['lang']
        } for sub in subs if sub['status_display'] == 'Accepted']

    def get_problems_dict(self):
        """Get the problem id, title and url from Leetcode,
        and parse it to dictionary.
        For example:
            {'1': {'title': 'value', 'url': 'value'}}
        """
        problems_url = self.BASE_URL + '/api/problems/algorithms'
        rep = self.__session.get(problems_url)
        rep_data = rep.json()
        stat_status_paris = rep_data['stat_status_pairs']
        problem_dict = {}
        for pair in stat_status_paris:
            problem_dict[pair['stat']['question_id']] = {
                'title': pair['stat']['question__title'],
                'url': pair['stat']['question__title_slug']
            }
        if not problem_dict:
            raise Exception('Not able to get problems, check your network')
        self.__problems = problem_dict

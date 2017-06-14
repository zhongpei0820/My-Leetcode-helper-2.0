"""This module generates the file name, formats the description
and code.
"""

#
#   Author: zhongpei
#
#   Date: 06/12/2017
#

import re
from collections import namedtuple


CommentExt = namedtuple('CommentExt', 'comment, ext')

COMMENTEXT = {
    'python': CommentExt(comment='#', ext='py'),
    'java': CommentExt(comment='//', ext='java'),
    'c++': CommentExt(comment='//', ext='cpp'),
    'c': CommentExt(comment='//', ext='c'),
    'csharp': CommentExt(comment='//', ext='cs'),
    'javascript': CommentExt(comment='//', ext='js'),
    'ruby': CommentExt(comment='#', ext='rb'),
    'swift': CommentExt(comment='//', ext='swift'),
    'golang': CommentExt(comment='//', ext='go')
}


def path_formatter(problem_id, title, lang):
    """Generate file path according to programming language.

    Args:
        title: the title of the problem,
        lang: programming language.

    Returns:
        A tuple of string representing the fromatted file path and file name.
    """
    new_title = title.replace(' ', '_')
    prefix = '%03d' % (problem_id)
    new_file_name = prefix + '_' + new_title + '.' + COMMENTEXT[lang].ext
    if problem_id < 100:
        path_name = '/%s/1-99/' % (lang.title())
    else:
        mod = problem_id / 100
        path_name = '/%s/%d00-%d99/' % (lang.title(), mod, mod)
    # path = '/%s/%s' % (path_name, new_file_name)
    return path_name, new_file_name


def description_formatter(description, lang):
    """Format description, add comment symbol to
    the head of each line.

    Args:
        description: unformatted description containing
        '\n\r',
        lang: programming language.

    Returns:
        A string representing the fromatted description.
    """
    lines = description.split('\n')
    commented_lines = [COMMENTEXT[lang].comment + line for line in lines]
    return '\n'.join(commented_lines) + '\n\n'


def code_formatter(code):
    """Format the code, convert ascii to char.

    Args:
        code: unformatted code containing ascii.

    Returns:
        A string representing the formatted code.
    """
    # filter ascii using regEx
    match = re.findall('(\\\\u[a-fA-F0-9]{4})', code)
    for string in set(match):
        # convert ascii to char, e.g. '\u003D' --> int(003D, 16) --> '='
        code = code.replace(string, chr(int(string[2:], 16)))
    return code

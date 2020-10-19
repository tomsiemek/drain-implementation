import re
from math import log
filename = ".\\logs\\Hadoop_2k.log" 

class Bubu:
    counter = 0
    def __init__(self):
        self.id = Bubu.counter
        Bubu.counter += 1

import re

def f1(string):
    return any(i.isdigit() for i in string)


def f2(string):
    return re.search('\d', string)


# if you compile the regex string first, it's even faster
RE_D = re.compile('\d')
def f3(string):
    return RE_D.search(string)

example_log = "205.189.154.54 - - [01/Jul/1995:00:01:19 -0400] \"GET /shuttle/missions/sts-71/images/KSC-95EC-0423.txt HTTP/1.0\" 200 1224"
example_tokens = example_log.split()
ip_reg = re.compile(r'(/|)([0-9]+\.){3}[0-9]+(:[0-9]+|)(:|)')
def test_whole(string):
    return ip_reg.sub("<IP>", string)

def test_tokens(tokens):
    return [ip_reg.sub("<IP>",t) for t in tokens]


DIGITS_RE = re.compile('\d')
def contains_digits(string):
    return DIGITS_RE.search(string)

def calc_base_st_init(tokens):
    digits_count = 0
    for token in tokens:
        if contains_digits(token):
            digits_count += 1
    base = max(2, digits_count + 1)
    st_init = 0.5 * (len(tokens) - digits_count) / len(tokens)
    return (st_init, base)

def new_st(st_init, base, n):
    return min(1, st_init + 0.5 * log(n+1, base))

(st_init, base) = calc_base_st_init(example_tokens)

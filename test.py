import re
filename = ".\\logs\\Hadoop_2k.log" 

class Bubu:
    counter = 0
    def __init__(self):
        self.id = Bubu.counter
        Bubu.counter += 1

RE_D = re.compile('\d')
def f3(string):
    return RE_D.search(string)
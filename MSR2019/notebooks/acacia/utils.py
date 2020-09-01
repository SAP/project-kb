import logging
import re
from datetime import datetime
import subprocess
import traceback

# def execute_wait(cmd, cwd='/tmp', encoding='latin-1', timeout=None):
#     logging.debug("exec: {} (in dir: {})".format( cmd, cwd ) )
#     try:
#         process = subprocess.Popen(cmd.split(), cwd=cwd)
#         process.wait(timeout = timeout)
#         return process.stdout.decode(encoding).split('\n')
#     except Exception as e:
#         logging.error('Exception happened while running ' + cmd)
#         logging.error(str(e))
#         return False

def execute(cmd, cwd='/tmp', encoding='latin-1'):
    try:
        p2 = subprocess.Popen(cmd.split(), cwd=cwd, stdout=subprocess.PIPE)
        out, err = p2.communicate()
        if err:
            # traceback.print_exc()
            return None

        raw_output_list = out.decode(encoding).split('\n')
        return raw_output_list

    except Exception as e:
        # traceback.print_exc()
        return None

# def flatten_lists(container):
#     for i in container:
#         if isinstance(i, (list, tuple)):
#             for j in flatten_lists(i):
#                 yield j
#         else:
#             yield i

# def clean_and_split_str(string):
#     ''' Clean and split sentence into words '''
# #     string = string.encode('UTF-8')
#     strip_special_chars = re.compile("[^A-Za-z]+")
#     string = re.sub(strip_special_chars, " ", string)
#     return string.strip().split()

class LatexExporter():

    def __init__(self):
        self.data = set()

    def __str__(self):
        self.print()

    def save(self,k,v, comment=''):
        print('[' + k + '] ' + comment.strip() + ': ' + str(v))
        self.data.add((k,v,comment))

    def print(self):
        for d in self.data:
            if d[2]!='':
                print('\n% ' + str(d[2]))
            print('\\newcommand{\\' + str(d[0]) +'}{' + str(d[1]) + '\\xspace}')

    def to_file(self, filename):
        with open(filename,'w') as f:
            f.write('%\n% This file was auto-generated on ' + str(datetime.now()) +'\n%\n')
            for d in self.data:
                line = ''
                if d[2] != '':
                    line += '\n% ' + str(d[2]) + '\n'
                line += '\\newcommand{\\'+ d[0] + '}{' + str(d[1]) + '\\xspace}'
                print(line)
                f.write(line + '\n')

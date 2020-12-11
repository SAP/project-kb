# -*- coding: utf-8 -*-
import subprocess
import logging
import traceback
import random

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

def execute_l(cmd_l, cwd='/tmp', encoding='latin-1',timeout=None):
    raise Exception("Deprecated! Use Exec.run() instead")
    # try:
    #     p2 = subprocess.Popen(cmd_l, cwd=cwd, stdout=subprocess.PIPE)
    #     # p2.wait(timeout = timeout)
    #     out, err = p2.communicate()
    #     if err:
    #         traceback.print_exc()
    #         return None
        
    #     raw_output_list = out.decode(encoding).split('\n')
    #     return [ r for r in raw_output_list if r.strip() != '' ]
    # except subprocess.TimeoutExpired:
    #     print('Timeout exceeded (' + timeout + ' seconds)')
    #     return None
    # except Exception:
    #     traceback.print_exc()
    #     return None

def execute(cmd, cwd='/tmp', encoding='latin-1', timeout=None):
    raise Exception("Deprecated! Use Exec.run() instead")

    # return execute_l(cmd.split(), cwd, encoding, timeout)

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

# Donald Knuth's "reservoir sampling"
# http://data-analytics-tools.blogspot.de/2009/09/reservoir-sampling-algorithm-in-perl.html
def reservoir_sampling(input_list, N):
    sample = []
    for i, line in enumerate(input_list):
        if i < N:
            sample.append(line)
        elif i >= N and random.random() < N / float(i + 1):
            replace = random.randint(0, len(sample) - 1)
            sample[replace] = line
    return sample

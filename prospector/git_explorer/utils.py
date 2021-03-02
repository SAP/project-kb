import random


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

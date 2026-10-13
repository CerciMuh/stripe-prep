#!/bin/python3

import math
import os
import random
import re
import sys


#
# Complete the 'evaluateTransactions' function below.
#
# The function is expected to return a STRING_ARRAY.
# The function accepts STRING_ARRAY commands as parameter.
#

def evaluateTransactions(commands):
    # Write your code here
    pass

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    commands_count = int(input().strip())

    commands = []

    for _ in range(commands_count):
        commands_item = input()
        commands.append(commands_item)

    result = evaluateTransactions(commands)

    fptr.write('\n'.join(result))
    fptr.write('\n')

    fptr.close()

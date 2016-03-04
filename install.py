import os
path = os.path.dirname(os.path.abspath(__file__))

# build forunit starter

starter = '#!/usr/bin/python\n'
starter += '# -*- coding: utf-8 -*-\n'
starter += 'import sys\n'

# register the current directory for the forunit module import
starter += 'sys.path.append(\'' + path + '\')\n'

try:
    f = open('starterTemplate.py', 'r')
    starter += f.read()
    f.close()

    f = open('forunit', 'w')
    f.write(starter)
    f.close()

except IOError as e:
    print 'ERROR: ' + e.message

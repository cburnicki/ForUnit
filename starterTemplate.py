import os
import forunit
import sys

def printHelp():

    print ('-h, --help\t\tshow this help.\n'+
           '-cf [flag1,flag2,...]\tuse compiler flags\n'+
           '-lf [flag1,flag2,...]\tuse link flags\n'+
           'clean, --clean, -c\tremove test files created by forunit\n')

    exit()


for i, arg in enumerate(sys.argv[1:]):

    if arg == '-h' or arg == '--help':
        printHelp()

    elif arg == 'clean' or arg == '-c' or arg == '--clean':
        forunit.cleanup()
        exit()

    elif arg == '-cf':
        forunit.compilerFlags = sys.argv[i+2].split(',')

    elif arg == '-lf':
        forunit.linkFlags = sys.argv[i+2].split(',')

forunit.cwd = os.getcwd()
forunit.run()

import os
import TestFileParser
import subprocess
import makeFortran as maker
import ShellFormat

# Array that holds the names of the test files
testFileNames = []

# Array that holds the names of the tests
testNames = []

# names of the fortran test modules created by the parser
testModuleNames = []

# array of every test routine in every file
testRoutines = []

# overall number of tests (for all files)
numberOfTests = 0

# overall number of failed tests (for all files)
numberOfFailedTests = 0

# array of TestFileParser instances
parsers = []

# gfortran link flags
linkFlags = []

# gfortran compiler flags
compilerFlags = []

# the used fortran extension
fortranExtension = '.f03'

fortranExtensions = ['.f70', '.f90', '.f95', '.f03']

# current working directory
cwd = './'

# Finds all .fu test files in the path
def findTestFiles(path='./'):

    global fortranExtension

    foundExtensions = []

    # find all .fu testfiles
    filenames = os.listdir(path)
    for filename in filenames:
        s = filename[-3:]
        if s == '.fu':
            testName = filename[:-3]
            print 'found test '+filename
            # found a forunit testfile, search for the module
            foundExtensions.append(findOriginalModule(testName))

            testFileNames.append(filename)
            testNames.append(testName)
    if len(testFileNames) == 0:
        print 'Did not find any .fu test files.\n'
        exit()

    # make sure there is only one file extension
    if len(foundExtensions) == 0:

        # no fortran module found
        message = 'Did not find a fortran module with a valid file extension: ' + ', '.join(fortranExtensions)
        runtimeError(message)
        exit()

    elif len(foundExtensions) > 1:

        # found more than one module
        message = 'Found fortran modules with different fortran extensions: ' + '(' + ' '.join(fortranExtensions) + ').'
        runtimeError(message)
        exit()

    else:

        fortranExtension = foundExtensions[0]


# looks for testName.f70, testName.f90, ...
# and returns the extensions of the found file
#
def findOriginalModule(testName):

    global fortranExtensions

    foundExtensions = []

    for extension in fortranExtensions:

        try:
            f = open(testName+extension)
            foundExtensions.append(extension)
        except IOError:
            pass

    if len(foundExtensions) == 0:

        # no fortran module found
        message = 'Did not find a fortran module for test ' + testName + ' using extensions ' + ', '.join(fortranExtensions)
        runtimeError(message)
        exit()

    elif len(foundExtensions) > 1:

        # found more than one module
        message = 'Found more than one fortran file for test: ' + testName + '(' + ' '.join(fortranExtensions) + ').'
        runtimeError(message)
        exit()

    else:

        return foundExtensions[0]

# prints an error message
def runtimeError(message):

    print ShellFormat.ERROR + 'ERROR: ' + message + '\n'

# Creates the fortran program TestRunner that will call every test subroutine
#
def createTestRunner():
    s = 'program TestRunner\n'

    # use every test module
    for moduleName in testModuleNames:
        s += '\tuse '+moduleName+'\n'

    s += '\n\timplicit none\n\n'

    # for every parsed test, call its test routines and teardown routines if one exists
    for parser in parsers:

        for testRoutine in parser.testRoutines:
            s += '\tcall '+testRoutine+'()\n'

            if parser.hasTeardown == True:
                s += '\tcall ' + parser.subroutinePrefix + 'teardown()\n'

    # print a FINISHED statement so the executing python program knows when the TestRunner finished testing
        s += '\n\tWRITE(*,*) "FINISHED TESTRUNNER"'

    s += '\nend program TestRunner'

    f = open('TestRunner'+fortranExtension, 'w')
    f.write(s)
    f.close()

    print 'created TestRunner'+fortranExtension

# This method uses the makeFortran module to create a makefile for the TestRunner
def createMakeFile():
    maker.target = 'TestRunner'
    maker.makeFileName = 'makeTestRunner'

    maker.createMakeFile()

# Compiles the tests using make
def compileTests():
    output = subprocess.call('make -f makeTestRunner', shell=True)

    return output

# Starts the test runner to run every test and parse the returned outcome
def runTestRunner():
    p = subprocess.Popen(['./TestRunner.exe'], stdout=subprocess.PIPE)

    output = []

    # collect output lines until TestRunner prints the keyword FINISHED
    while True:
        line = p.stdout.readline()

        if 'FINISHED TESTRUNNER' in line:
            break

        output.append(line)


    p.kill()

    # parse the collected test results for FAILED statements
    parseTestResults(output)

    return output

# Deletes all files created by this test environment
def cleanup():
    deleteList = ['TestRunner.o', 'TestRunner'+fortranExtension, 'TestRunner.exe']
    for testModule in testModuleNames:
        deleteList.append(testModule+fortranExtension)
        deleteList.append(testModule+'.o')

    deleteList.append('makeTestRunner')
    o = subprocess.call('rm '+' '.join(deleteList))

# Counts and prints FAILED statements of TestRunner
def parseTestResults(output):

    global numberOfFailedTests

    for line in output:

        if line.find('FAILED') > -1:
            numberOfFailedTests += 1
            print ShellFormat.ERROR + line + ShellFormat.END

        else:
            print line

# Prints a summary of the test results
def printOverallResult():

    global numberOfFailedTests
    global numberOfTests

    if numberOfFailedTests != 0:
        msg = ShellFormat.BOLD + ShellFormat.ERROR + str(numberOfFailedTests) + ' OUT OF ' + str(numberOfTests) + ' TESTS FAILED!' + ShellFormat.END + '\n'

    else:
        msg = ShellFormat.BOLD + ShellFormat.OKGREEN + 'ALL ' + str(numberOfTests) + ' TESTS PASSED!' + ShellFormat.END + '\n'

    print '+'*100+'\n'
    print msg

def run():

    global numberOfTests
    global testModuleNames
    global testRoutines
    global parsers
    global testFileNames
    global cwd

    print ShellFormat.OKBLUE + ShellFormat.BOLD + 'RUNNING FORUNIT TESTSUITE' + ShellFormat.END

    findTestFiles(cwd)

    print 'parsing test files...'

    # parse each test file
    for testFileName in testFileNames:
        parser = TestFileParser.TestFileParser(testFileName)
        parser.parseTestFile()

        parsers.append(parser)
        testModuleNames.append(parser.fortranModuleName)
        testRoutines.extend(parser.testRoutines)
        numberOfTests += parser.numberOfTests

        print 'created test '+parser.testName+' as '+parser.fortranTestfileName

    createTestRunner()
    createMakeFile()

    print '\n'+'+'*100+'\n\ncompiling...\n'

    print compileTests()

    print 'run TestRunner...\n\n'

    runTestRunner()


    printOverallResult()

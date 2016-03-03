import ShellFormat

class TestFileParser():

    def __init__(self, testFileName, fortranVersion = '03'):
        # filename of the test file (*.fu)
        self.testFileName = testFileName
        # name of the test in the .fu file
        self.testName = testFileName[:-3]

        self.fortranFileExtension = '.f'+fortranVersion

        # name of the test module contains the name of the module to test + a constant
        self.fortranModuleName = self.testName + 'ForUnitTest'
        self.fortranTestfileName = self.fortranModuleName + self.fortranFileExtension

        # prefix of the test subroutines that will be created by this parser
        self.subroutinePrefix = 'test_'+self.testName+'_'

        # number of tests found in this test file
        self.numberOfTests = 0

        # the name of the test routine the parser is currently in
        self.currentTestRoutine = ''

        # a list of test routines created by the parser
        self.testRoutines = []

        # the number of the currently parsed line
        self.currentLine = 0

        # a list of modules on that this module and its children depend
        self.dependencies = []

        # true if currently in teardown routine
        self.inTeardown = False

        # true if the test file has a teardown routine
        self.hasTeardown = False

        # counts parse errors
        self.numberOfParseErrors = 0

    # prints a parser error
    def parserError(self, message):
        errMsg = ShellFormat.ERROR + 'PARSE ERROR: '
        errMsg += message + ' in file ' + self.testFileName
        errMsg += ' on line ' + str(self.currentLine)
        errMsg += ShellFormat.END

        self.numberOfParseErrors += 1

        print errMsg

        return errMsg

    # opens a test file and parses it one line at a time
    def parseTestFile(self):

        try:
            f = open(self.testFileName, 'r')
        except IOError as e:
            print ShellFormat.ERROR + 'Failed to open test file: '+self.testFileName+ShellFormat.END
            print '\t I/O error({0}): {1}'.format(e.errno, e.strerror)
            return

        # holds the content of the fortran file to create
        testModuleContent = ''
        testModuleContentBody = ''

        # now parse the test code into it:

        self.currentLine = 0

        for line in f.readlines():
            self.currentLine += 1

            # add the parsed line
            testModuleContentBody += self.getParsedLine(line)

        f.close()

        # add the head of the fortran file
        testModuleContent += self.getTestHead()

        # add the parsed content of the fortran file
        testModuleContent += '\n\ncontains\n\n'
        testModuleContent += testModuleContentBody

        # add the foot of the fortran file
        testModuleContent += self.getTestFoot()

        # write it all to a new fortran test module
        f = open(self.fortranTestfileName, 'w')
        f.write(testModuleContent)
        f.close()

    # builds a head for the fortran test module
    def getTestHead(self):
        head = 'module '+self.fortranModuleName+'\n'
        head += 'use '+self.testName+'\n\n'
        head += 'implicit none\n\n'
        return head

    # builds a head for the fortran test module
    def getTestFoot(self):
        return 'end module '+self.fortranModuleName

    # creates a test to assert two arrays equal (shape and content)
    def createAssertArrayEqualTest(self, line):

        line = line.strip()
        i = len('assert_array_euqal(')
        # remove the "assert_array_equal(" statement
        line = line[i:]

        # find both var names
        commaPos = line.find(',')
        array1 = line[:commaPos].strip()
        # second will end one character before the line end ")"
        array2 = line[commaPos+1:-1].strip()

        # error message
        msg = 'shape of '+array1+' does not match shape of '+array2

        # the actual fortran test logic
        test = '\tif ( .not. all( shape('+array1+') == shape('+array2+') ) ) then\n'
        test += self.createFortranErrorMessage('assert array equal', msg)
        test += '\tend if\n\n'

        msg = array1+' does not match '+array2

        test += '\tif ( .not. all('+array1+' == '+array2+') ) then\n'
        test += self.createFortranErrorMessage('assert array equal', msg)
        test += '\tend if\n\n'

        self.numberOfTests += 1

        return test

    # creates a test to assert a variable true
    def createAssertTrueTest(self, line):

        line = line.strip()
        i = len('assert_true(')

        # get the var name
        var = line[i:-1].strip()

        msg = var + ' is not TRUE'

        # fortran test logic
        test = '\tif ( .not. '+var+' ) then\n'
        test += self.createFortranErrorMessage('assert true', msg)
        test += '\tend if\n\n'

        self.numberOfTests += 1

        return test

    # create a test to assert a variable false
    def createAssertFalseTest(self, line):

        line = line.strip()

        # get the var name
        i = len('assert_false(')
        var = line[i:-1]

        msg = var + ' is not FALSE'

        # fortran test logic
        test = '\tif ( '+var+' ) then\n'
        test += self.createFortranErrorMessage('assert false', msg)
        test += '\tend if\n\n'

        self.numberOfTests += 1

        return test

    # create a test that asserts two variables equal
    # @todo: for type real, there should also be an "in_range_validation"...
    def createAssertEqualTest(self, line):

        line = line.strip()

        # get the names of the two variables
        i = len('assert_false(')
        commaPos = line.find(',')
        var1 = line[i:commaPos].strip()
        var2 = line[commaPos+1:-1].strip()

        msg = var1 + '(", ' + var1 + ', ") does not equal ' + var2 + '(", ' + var2 + ', ")'

        # fortran test logic
        test = '\tif ( '+var1+'/= '+var2+' ) then\n'
        test += self.createFortranErrorMessage('assert false', msg)
        test += '\tend if\n\n'

        return test

    # This method creates a fortran statement that prints an error message if a test fails.
    #
    # THE KEYWORD "FAILED" is later being used to determine test failures in the output stream of
    # the fortran TestRunner!
    #
    def createFortranErrorMessage(self, assertType, message = None):
        errMsg = '\t\t write(*,*) "FAILED '+assertType+' TEST '
        errMsg += '('+self.currentTestRoutine+') '
        errMsg += 'in test '+self.testFileName

        if message != None:
            errMsg += ': ", & \n\t\t"'+message

        errMsg += '."\n'

        errMsg += '\t\t WRITE(*,*) "on line ' + str(self.currentLine) + ' in file ' + self.testFileName + '"\n'

        return errMsg

    # parses on line of the test file and replaces asserts with the according fortran code
    def getParsedLine(self, line):
        newLine = ''

        # Line starts with a "test" statement:
        #   Create a new test subroutine...
        #
        if line.strip()[0:5] == 'test ':

            # start subroutine, check if the parser is currently in a subroutine
            if self.currentTestRoutine != '':
                self.parserError(' Can\'t begin a new test subroutine inside another test subroutine!')

            # get the name of the test routine that follows the test statement
            routineName = line[5:].strip()

            # create a new subroutine
            newLine += 'subroutine '+ self.subroutinePrefix + routineName + '()\n'

            # tell parser, that it now is inside a subroutine
            self.currentTestRoutine = routineName
            self.testRoutines.append(self.subroutinePrefix + routineName)

            return newLine

        # Line starts with an "end test" statement:
        #   Leave the current test subroutine...
        #
        elif line.strip()[0:8] == 'end test':

            # check if the parser currently is in a subroutine
            if self.currentTestRoutine == '':
                self.parserError('Can\'t leave subroutine without being in a subroutine!')

            # leave the fortran subroutine
            newLine += 'end subroutine ' + self.subroutinePrefix + line[9:].strip()+'\n\n'

            # tell the parser that it is not inside of a subroutine anymore
            self.currentTestRoutine = ''

            return newLine

        # Line starts with an "end teardown" statement:
        #   Leave teardown subroutine...
        #
        #   Teardown subroutines are called after every test subroutine call.
        #
        elif line.strip().find('end teardown') > -1:

            # Check if the parser is currently in a teardown
            if not self.inTeardown:
                self.parserError('Teardown ended before it started.')

            # Tell parser that it left the teardown routine
            self.inTeardown = False

            # leave the fortran teardown subroutine
            newLine += 'end subroutine ' + self.subroutinePrefix + 'teardown\n'

            return newLine

        # Line starts with a "teardown" statement:
        #   Create a new teardown subroutine...
        #
        #   Teardown subroutines are called after every test subroutine call.
        #
        elif line.strip().find('teardown') > -1:

            # check that the parser is currently not inside a teardown routine
            if self.inTeardown:
                self.parserError('teardown routine defined more than once')
                return

            self.inTeardown = True
            self.hasTeardown = True

            newLine += 'subroutine ' + self.subroutinePrefix + 'teardown()\n'

            return newLine

        # Found some assert statement...
        elif line.find('assert_') > -1:

            newLine = self.getParsedAssertStatement(line)

            return newLine

        # Just return the fortran code / comment / etc
        else:
            newLine += line

        return newLine

    # If the parser found an "assert_" statement, this methods makes further decisions
    #
    def getParsedAssertStatement(self, line):

        # Check if the parser is currently in a teardown method
        if self.inTeardown:
            self.parserError('Assert statements are not allowed inside the teardown method!')

            return line

        # Check if the parser is currently inside a subroutine
        if self.currentTestRoutine == '':
            self.parserError('Assert statements are only allowed inside test routines!')

            return line

        # Create an assert array equal test
        if line.find('assert_array_equal') > -1:

            newLine = self.createAssertArrayEqualTest(line)

            return newLine

        # Create an assert true test
        elif line.find('assert_true') > -1:
            newLine = self.createAssertTrueTest(line)

            return newLine

        # Create an assert false test
        elif line.find('assert_false') > -1:
            newLine += self.createAssertFalseTest(line)

            return newLine

        # Create an assert equal test
        elif line.find('assert_equal') > -1:
            newLine = self.createAssertEqualTest(line)

            return newLine
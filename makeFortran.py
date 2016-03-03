#
# Given a target, this module creates a makefile for a fortran project.
# You may also set an array of compilerFlags resp. linkFlags
#

# name of the target (without file extension)
target = ''

# name of the makefile
makeFileName = 'makefile'

# some compiler flags that should be used
compilerFlags = []

# some link flags that should be used
linkFlags = []

# Array of strings. Holds formatted target and rule entries of the makefile
entries = []

# List of allowed fortran file extension
fortranFileExtensions = ['.f03', '.f95', '.f90']

# The fortran file extension that will actually be used
fortranFileExtension = ''

# A list of dependencies all the way down from target to its nth child
dependencies = []

# Finds the fortran file extension if not given
def findFileExtension():

    global fortranFileExtensions
    global target
    global fortranFileExtension

    for extension in fortranFileExtensions:
        try:
            f = open(target+extension)
            # set this as the used fortran file extension
            fortranFileExtension = extension
            break
        except IOError as e:
            pass

    if fortranFileExtension == '':
        print 'ERROR: Couldn\'t find a fortran file for target '+target

# Iteratively searches for dependencies of target and creates makefile entires on the fly
def getDependencies(filename):

    global dependencies
    global fortranFileExtension

    # open a fortran file
    f = open(filename, 'r')

    newDependencies = []

    # get dependencies in this file
    for line in f.readlines():

            pos = line.find('use ')
            if pos > -1:
                dependency = line[pos+4:].strip()
                newDependencies.append(dependency)

    # look for subdependencies
    for dependency in newDependencies:

        # iteratively look into used files
        subdependencies = getDependencies(dependency+fortranFileExtension)
        newDependencies.extend(subdependencies)

        # create a link rule fpr this file and its direct dependencies
        linkRule = createEntryForLinkFile(dependency, subdependencies)
        if linkRule not in entries:
            entries.append(linkRule)

        if dependency not in dependencies:
            dependencies.append(dependency)

    return newDependencies

# creates a makefile entry for a *.o file
def createEntryForLinkFile(target, dependencies = []):

    global compilerFlags

    # target and dependencies
    s = target + '.o: '+target+fortranFileExtension+' '

    for dependency in dependencies:
        s += dependency + '.o '

    # rule:
    s += '\n\tgfortran -c ' + ' '.join(compilerFlags) + ' ' + target + '.f03\n\n'

    return s

# creates the makefile entry for the main target
def createMainTargetEntry(target, dependencies = []):

    global linkFlags

    # target
    s = target+'.exe: '

    # dependencies
    for dependency in dependencies:
        s += dependency + '.o '

    s += target+'.o '

    # link rule
    s += '\n\tgfortran ' + ' '.join(linkFlags) + ' '

    for dependency in dependencies:
        s += dependency + '.o '

    s += ' '+target+'.o '

    s += ' -o '+target+'.exe\n\n'

    return s

# creates the make clean target
def createCleanRule():

    s = 'clean:\n\trm '
    # delete all .mod files
    s += '.mod '.join(dependencies).lower()+'.mod '

    # delete all .o files
    s += '.o '.join(dependencies) + '.o '
    s += target+'.o '+target+'.exe '

    return s

# main method to create a makefile for the target
def createMakeFile():

    global fortranFileExtension

    if fortranFileExtension == '':

        findFileExtension()

    # collect dependencies and create targets for their link files
    getDependencies(target+fortranFileExtension)

    # create all target with executable as dependency
    fileContent = 'all: '+target+'.exe\n\n'

    # create target executable with link files as dependencies
    fileContent += createMainTargetEntry(target, dependencies)

    # create target for the executables link file
    fileContent += createEntryForLinkFile(target, [])

    fileContent += ''.join(entries)

    # create the make clean target and rule
    fileContent += createCleanRule()

    # write everything into the makefile
    f = open(makeFileName, 'w')
    f.write(fileContent)
    f.close()



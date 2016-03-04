# makeFortran
A simple module that, given a fortran file as a target, looks up every dependency and creates a makefile.

Given a target, this module creates a makefile for a fortran project.
You may also set an array of compilerFlags resp. linkFlags.

# Example:

import makeFortran as maker

maker.target = 'TestRunner'
maker.compilerFlags = ['-g']
maker.linkFlags = ['-g']
maker.createMakeFile()

creates the makefile for TestRunner.f03 and its dependencies

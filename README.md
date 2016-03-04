# ForUnit
Despite the fact that there are some fortran unit test suites out there, I thought some of them were too complicated in their syntax or simply ran out of maintenance. One that I particularly liked because its syntax was very easy is NASA's FUnit (http://nasarb.rubyforge.org/). However, it was designed to work with fortran90 and does not work with fortran2003. 

FUnit is written in ruby. Since I don't know ruby and had a bit of time, I decided to write an own unit test suite in python.
The test file syntax and the usage of this suite is very close to that of FUnit. 
And that's that. I need it to test code for my bachelors thesis, therefore it is sure missing some functionality (as well as some assert statements that I did not need so far) and has yet to be broadly tested. 

So don't use it to test any security sensitive code.

However, if someone else wants to use it: You are very welcome to contribute!

##Usage

Suppose you have a fortran module named Network.f03 (or .f70, .f90, .f95). Simply create another file Network.fu in the same directory. Now you would only have to run the command `forunit` to execute every .fu unit test in that directory and get a summary of your test results.

The content of Network.fu could be as follows:
```
test add_edge
  integer :: edges_added(3,2)
  
  ! call subroutine add_edge() of module Network
  ! add_edges() will add the edges to a (:,2) integer array named edges
  call add_edge(1,3)
  call add_edge(1,4)
  call add_edge(2,4)
  
  edges_added = reshape((/1,1,2,3,4,4/),(/3,2/))
  
  ! edges is the modules own array
  assert_array_equal(edges,edges_added)
end test

teardown
  call remove_all_edges()
end teardown
```
The teardown routine will be executed after each test. ForUnit will now parse all your testfiles, fook for the original modules to test, parse them to turn every test into a subroutine and every assert statement into the according fortran code. All of that will be placed into a wrapping fortran module that uses the original module. After that, a TestRunner.f03 will be created and compiled. TestRunner uses every test module and calls their test routine. The output will then be parsed and analized.

The command foruni clean will delete all files created by forunit.

Current assert statements are:
```
  assert_array_equal()
  assert_equal()
  assert_true()
  assert_false()
```

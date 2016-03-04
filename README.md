# ForUnit
Despite the fact that there are some fortran unit test suites out there, I thought some of them were too complicated in their syntax or simply ran out of maintenance. One that I particularly liked because its syntax was very easy is NASA's FUnit (http://nasarb.rubyforge.org/). However, it was designed to work with fortran90 and does not work with fortran2003. 

FUnit is written in ruby. Since I don't know ruby and had a bit of time, I decided to write an own unit test suite in python. And that's that. I need it to test code for my bachelors thesis, therefore it is sure missing some functionality (as well as some assert statements that I did not need so far) and has yet to be broadly tested. 

So don't use it to test any security sensitive code.

However, if someone else wants to use it: You are very welcome to contribute!


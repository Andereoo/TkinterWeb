#!/bin/bash
# Run this with Mingw



rm -rf tkhtml3
git clone https://github.com/olebole/tkhtml3.git

cd tkhtml3

# 32-bit MinGW
#TCL=/c/Tcl 
#export PATH=/c/MinGW/mingw32/bin:$PATH


# 64-bit Msys2, run from Mingw64 shell
TCL=/c/Tcl_64-bit 


export PATH=$TCL/bin:$PATH





# Generate some source files (see readme in https://github.com/starseeker/tcltk/tree/master/tkhtml)
tclsh src/cssprop.tcl
tclsh src/tokenlist.txt
tclsh src/mkdefaultstyle.tcl > htmldefaultstyle.c

# copy these generated files to src
mv *.c src
mv *.h src

# create build dir
mkdir build
cd build


../configure CC="gcc -static-libgcc" \
    --with-tcl=$TCL/lib \
    --with-tk=$TCL/lib \
    --with-tclinclude=$TCL/include \
    --with-tkinclude=$TCL/include

make binaries

# For getting 64-bit version, I had to change the generated Makefile
# For some reason SHLIB_LD was left empty
# I set this to  
#     gcc -static-libgcc -pipe -shared
# deleted all *.o files and ran make again
# NB! the dll was created without ".dll" extension!
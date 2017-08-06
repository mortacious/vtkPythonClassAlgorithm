## Goal
This module works like the build-in "Programmable Source" and "Programmable Filter" commands, except that the Python code is kept in an external file.

## How to compile
Build using cmake, see the first line of CMakeLists.txt for the cmake command I use to build

## Tested on
macOS Sierra with Python 2.7.13 and 3.6.1

## How to use the example module:
1. Add the directory containing example.py to the PYTHONPATH environment variable when starting pvserver or paraview
2. Create a "Python Class Source" from the "Sources" menu
3. Set Module property to "example" (there will be some waiting after this as ParaView loads the vtk python module)
4. Set Class property to "SinSource"
5. When displaying the resulting Source in the Line Chart View, you should see a period of a sine wave

## Caveats:
vtkPythonAlgorithm will crash if the vtk python module or one of its submodules has not been imported when the first request comes in. To prevent this, always add an "import vtk" line to your modules.

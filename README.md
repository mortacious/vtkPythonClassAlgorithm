## Goal
This module works like the build-in "Programmable Source" and "Programmable Filter" commands, except that the Python code is kept in an external file.
It takes a Python module and class name as properties. On each execution of the pipeline (in the `REQUEST_DATA_OBJECT` pass), a Python object of the specified class is instantiated. For each pipeline pass, the `processRequest` method of the created object is called.

Keeping the Python code in an external file has the advantage that the contents stay intact when ParaView crashes due to a coding error (e.g. forgetting to allocate cells in a vtkPolyLine()).
The code can furthermore be edited with a standard editor and is easily redistributed.

Using a Python object enables the use of parent classes to build simplified APIs (e.g. the `Algorithm` class in `example.py`). It also keeps the code for the RequestData and RequestInformation passes in one place. Finally, it might be useful to share data between Pipeline passes (for example when implementing a Reader).

## Some Implementation Details
* This class inherits from vtkPythonAlgorithm, but is unlikely to keep doing so in the future. 

* The VTK algorithm objects are created with 1 optional input port and 1 output port. 

* The Python module is reloaded on every `REQUEST_DATA_OBJECT` pass.

## How to compile
Build using cmake, see the first line of CMakeLists.txt for the cmake command I use to build

## Tested on
macOS Sierra with Python 2.7.13 and 3.6.1

## How to use the example module:
1. Add the directory containing example.py to the PYTHONPATH environment variable before starting pvserver or paraview
2. Load the Plugin (Tools->Manage Plugins)
3. Create a "Python Class Source" from the "Sources" menu
4. Set Module property to "example" (there will be some waiting after this as ParaView loads the vtk python module)
5. Set Class property to "SinSource"
6. When displaying the resulting Source in the Line Chart View, you should see a period of a sine wave

## Caveats:
vtkPythonAlgorithm will crash if the vtk python module or one of its submodules has not been imported when the first request comes in (because no VTK classes have yet been registered with some subsystem that tries to find the matching Python class for a VTK class, or vice versa). To prevent this, always include an "import vtk" line with your modules.

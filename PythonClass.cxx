#include <vtkSmartPointer.h>

#include "vtkPythonInterpreter.h"
#include "vtkPythonUtil.h"
#include "vtkPythonClassAlgorithm.h"

//#include "pvpythonmodules.h"
//#include "vtkUtilitiesPythonInitializerModule.h"

int main(int, char *[])
{
    vtkPythonInterpreter::PrependPythonPath("/Applications/paraview.app/Contents/Python");
    vtkPythonInterpreter::PrependPythonPath("/Users/bob.pepin/Documents/Paraview/ParaView-build/lib");
    vtkPythonInterpreter::PrependPythonPath(".");
    vtkPythonInterpreter::Initialize();
    PyImport_ImportModule("vtkCommonCorePython");
#if 0
    vtkPythonClassAlgorithm* source = vtkPythonClassAlgorithm::New();
    source->SetPythonModuleName("foo");
    source->SetPythonClassName("SinSource");
    
    vtkPythonClassAlgorithm* filter = vtkPythonClassAlgorithm::New();
    filter->SetPythonModuleName("foo");
    filter->SetPythonClassName("MulFilter");
    filter->SetInputConnection(0, source->GetOutputPort(0));

    vtkPythonClassAlgorithm* sink = vtkPythonClassAlgorithm::New();
    sink->SetPythonModuleName("foo");
    sink->SetPythonClassName("PrintSink");
    sink->SetInputConnection(0, filter->GetOutputPort(0));
    
    sink->Update();
#endif
    vtkPythonClassAlgorithm* source = vtkPythonClassAlgorithm::New();
    source->SetPythonModuleName("foo");
    source->SetPythonClassName("ParamSource");
    source->SetParameter("bla", 23);
    source->SetParameter1("foo");
    return EXIT_SUCCESS;
}

#include "vtkPython.h"

#include "vtkPythonClassAlgorithm.h"
#include "vtkPythonAlgorithm.h"
#include "vtkObjectFactory.h"

#include "vtkDemandDrivenPipeline.h"
#include "vtkDataObject.h"
#include "vtkInformation.h"
#include "vtkInformationVector.h"
#include "vtkPythonUtil.h"
#include "vtkPythonInterpreter.h"
#include "vtkSmartPyObject.h"

/* TODO:
   Handle errors when loading module
   Handle errors when wrong module or class name
 */

vtkStandardNewMacro(vtkPythonClassAlgorithm);

void vtkPythonClassAlgorithm::PrintSelf(ostream& os, vtkIndent indent)
{
  this->Superclass::PrintSelf(os,indent);

  os << indent << "Python Class: " << ClassName << std::endl;
#if 0
  if (this->Module)
  {
    os << indent << "Module (string): ";
#ifndef VTK_PY3K
    os << PyString_AsString(Module);
#else
    PyObject *bytes = PyUnicode_EncodeLocale(Module, VTK_PYUNICODE_ENC);
    if (bytes)
    {
      os << PyBytes_AsString(bytes);
      Py_DECREF(bytes);
    }
#endif
    os << std::endl;
  }
#endif
}

vtkPythonClassAlgorithm::vtkPythonClassAlgorithm()
{
  this->Module = 0;
  this->Object = 0;
  this->ClassName = "";
  this->ModuleName = "";
  this->SetNumberOfInputPorts(1);
  this->SetNumberOfOutputPorts(1);
  if (!vtkPythonInterpreter::IsInitialized()) {
    vtkPythonInterpreter::Initialize();
  }
  this->PropertyDict = PyDict_New();
}

vtkPythonClassAlgorithm::~vtkPythonClassAlgorithm()
{
  if(Py_IsInitialized()) {
    Py_XDECREF(this->PropertyDict);
    Py_XDECREF(this->Module);
  }
}

void vtkPythonClassAlgorithm::SetPythonModuleName(const char* name)
{
  this->ModuleName = name;
  if(this->ModuleName.length() > 0) {
      this->Module = PyImport_ImportModule(this->ModuleName.c_str());
      if(this->Module) {
          InstantiatePython();
      } else {
          PyErr_Print();
      }
  }
}

void vtkPythonClassAlgorithm::SetPythonClassName(const char* name)
{
  this->ClassName = name;
  InstantiatePython();
}

void vtkPythonClassAlgorithm::UpdateProperties()
{
    if(!this->Module || !this->Object || !this->PropertyDict)
	return;
    PyObject *r = PyObject_CallMethod(this->Object, "UpdateProperties", "O", PropertyDict);
    if(!r)
	PyErr_Print();
    this->Modified();    
}

void vtkPythonClassAlgorithm::SetStringProperty(const char* name, const char* value)
{
    if(!this->Module || !this->Object || !this->PropertyDict)
	return;
    PyObject *valobj = PyUnicode_FromString(value);
    PyDict_SetItemString(PropertyDict, name, valobj);
    Py_XDECREF(valobj);
    this->UpdateProperties();
}

void vtkPythonClassAlgorithm::InstantiatePython()
{
  if(!this->Module)
    return;
  if(!PyObject_HasAttrString(this->Module, this->ClassName.c_str()))
     return;
  PyObject* instance = PyObject_CallMethod(this->Module,
					   const_cast<char*>(this->ClassName.c_str()),
					   0);
  if(instance) {
    this->SetPythonObject(instance);
    this->Object = instance;
    UpdateProperties();
  } else {
    PyErr_Print();
  }

}

int vtkPythonClassAlgorithm::ProcessRequest(vtkInformation* request,
                                       vtkInformationVector** inInfo,
                                       vtkInformationVector* outInfo)
{
  if(!this->Module)
    return 1;

  if(request->Has(vtkDemandDrivenPipeline::REQUEST_DATA_OBJECT())) {
    if(PyImport_ReloadModule(this->Module)) {
      InstantiatePython();
    } else {
      PyErr_Print();
    }
  }
  this->Superclass::ProcessRequest(request, inInfo, outInfo);
  return 1;
}

int vtkPythonClassAlgorithm::FillInputPortInformation(int port, vtkInformation* info)
{
  if(port == 0) {
    info->Set(vtkAlgorithm::INPUT_IS_OPTIONAL(), 1);
  }
  
  if(this->Module) {
    this->Superclass::FillInputPortInformation(port, info);
  }
  
  return 1;
}

int vtkPythonClassAlgorithm::FillOutputPortInformation(int port, vtkInformation* info)
{
  info->Set(vtkDataObject::DATA_TYPE_NAME(), "vtkDataObject");
  this->Superclass::FillOutputPortInformation(port, info);
  return 1;
}

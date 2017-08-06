/*=========================================================================

  Program:   Visualization Toolkit
  Module:    vtkPythonAlgorithm.h

  Copyright (c) Ken Martin, Will Schroeder, Bill Lorensen
  All rights reserved.
  See Copyright.txt or http://www.kitware.com/Copyright.htm for details.

     This software is distributed WITHOUT ANY WARRANTY; without even
     the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
     PURPOSE.  See the above copyright notice for more information.

=========================================================================*/
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
   Make it work with Python 2
   Handle errors when wrong module or class name
   Reinstantiate when module name changed
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

static std::string GetPythonErrorString()
{
  PyObject* type;
  PyObject* value;
  PyObject* traceback;

  // Increments refcounts for returns.
  PyErr_Fetch(&type, &value, &traceback);
  // Put the returns in smartpointers that will
  // automatically decrement refcounts
  vtkSmartPyObject sType(type);
  vtkSmartPyObject sValue(value);
  vtkSmartPyObject sTraceback(traceback);

  if (!sType)
  {
    return "No error from Python?!";
  }

  std::string exc_string;

  vtkSmartPyObject tbModule(PyImport_ImportModule("traceback"));
  if (tbModule)
  {
    vtkSmartPyObject formatFunction(PyObject_GetAttrString(tbModule.GetPointer(), "format_exception"));

    vtkSmartPyObject args(PyTuple_New(3));

    Py_INCREF(sType.GetPointer()); // PyTuple steals a reference.
    PyTuple_SET_ITEM(args.GetPointer(), 0, sType.GetPointer());

    Py_INCREF(sValue.GetPointer()); // PyTuple steals a reference.
    PyTuple_SET_ITEM(args.GetPointer(), 1, sValue.GetPointer());

    Py_INCREF(sTraceback.GetPointer()); // PyTuple steals a reference.
    PyTuple_SET_ITEM(args.GetPointer(), 2, sTraceback.GetPointer());

    vtkSmartPyObject formatList(PyObject_Call(formatFunction.GetPointer(), args, NULL));
    vtkSmartPyObject fastFormatList(PySequence_Fast(formatList.GetPointer(), "format_exception didn't return a list..."));

    Py_ssize_t sz = PySequence_Size(formatList.GetPointer());
    PyObject** lst = PySequence_Fast_ITEMS(fastFormatList.GetPointer());
    exc_string = "\n";
    for (Py_ssize_t i = 0; i < sz; ++i)
    {
      PyObject* str = lst[i];
#ifndef VTK_PY3K
      exc_string += PyString_AsString(str);
#else
      PyObject *bytes = PyUnicode_EncodeLocale(str, VTK_PYUNICODE_ENC);
      if (bytes)
      {
        exc_string += PyBytes_AsString(bytes);
        Py_DECREF(bytes);
      }
#endif
    }
  }
  else
  {
    vtkSmartPyObject pyexc_string(PyObject_Str(sValue));
    if (pyexc_string)
    {
#ifndef VTK_PY3K
      exc_string = PyString_AsString(pyexc_string);
#else
      PyObject *bytes = PyUnicode_EncodeLocale(
        pyexc_string, VTK_PYUNICODE_ENC);
      if (bytes)
      {
        exc_string = PyBytes_AsString(bytes);
        Py_DECREF(bytes);
      }
#endif
    }
    else
    {
      exc_string = "<Unable to convert Python error to string>";
    }
  }

  PyErr_Clear();

  return exc_string;
}

void vtkPythonClassAlgorithm::SetPythonModuleName(const char* name)
{
  this->ModuleName = name;
  this->Module = PyImport_ImportModule(this->ModuleName.c_str());
  if(this->Module) {
    InstantiatePython();
  } else {
    PyErr_Print();
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

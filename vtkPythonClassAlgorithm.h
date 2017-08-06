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
/**
 * @class   vtkPythonClassAlgorithm
 * @brief   algorithm that can be implemented in Python
 *
 * vtkPythonAlgorithm is an algorithm that calls a Python object to do the actual
 * work.
 * It defers the following methods to Python:
 * - ProcessRequest()
 * - FillInputPortInformation()
 * - FillOutputPortInformation()
 *
 * Python signature of these methods is as follows:
 * - ProcessRequest(self, vtkself, request, inInfo, outInfo) : vtkself is the vtk object, inInfo is a tuple of information objects
 * - FillInputPortInformation(self, vtkself, port, info)
 * - FillOutputPortInformation(self, vtkself, port, info)
 * - Initialize(self, vtkself)
 *
 * In addition, it calls an Initialize() method when setting the Python
 * object, which allows the initialization of number of input and output
 * ports etc.
 *
 * @sa
 * vtkProgrammableFilter
*/

#ifndef vtkPythonClassAlgorithm_h
#define vtkPythonClassAlgorithm_h

#include "vtkPython.h" // Must be first

#include "vtkFiltersPythonModule.h" // For export macro
#include "vtkPythonAlgorithm.h"

#include <string>
#include <iostream>

class VTKFILTERSPYTHON_EXPORT vtkPythonClassAlgorithm : public vtkPythonAlgorithm
{
public:
  static vtkPythonClassAlgorithm *New();
  vtkTypeMacro(vtkPythonClassAlgorithm, vtkPythonAlgorithm);
  void PrintSelf(ostream& os, vtkIndent indent) VTK_OVERRIDE;

  /**
   * Insert doc here
   */
  void SetPythonClassName(const char* name);
  void SetPythonModuleName(const char* name);
  void SetStringProperty(const char* name, const char* value);
  void ClearStringProperties() {
      std::cout << "ClearStringProperties\n";
      if(PropertyDict) {
	  PyDict_Clear(PropertyDict);
      }
  };

protected:
  vtkPythonClassAlgorithm();
  ~vtkPythonClassAlgorithm();

  int ProcessRequest(vtkInformation* request,
                     vtkInformationVector** inInfo,
                     vtkInformationVector* outInfo) VTK_OVERRIDE;
  int FillInputPortInformation(int port, vtkInformation* info) VTK_OVERRIDE;
  int FillOutputPortInformation(int port, vtkInformation* info) VTK_OVERRIDE;

  void UpdateProperties();
  void InstantiatePython();
  
private:
  vtkPythonClassAlgorithm(const vtkPythonClassAlgorithm&) VTK_DELETE_FUNCTION;
  void operator=(const vtkPythonClassAlgorithm&) VTK_DELETE_FUNCTION;
  
  PyObject* Module;
  PyObject* Object;
  PyObject* PropertyDict;
  std::string ClassName;
  std::string ModuleName;
};

#endif

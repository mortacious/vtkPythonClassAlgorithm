/**
 * @class   vtkPythonClassAlgorithm
 * @brief   algorithm that can be implemented in Python
 *
 * vtkPythonClassAlgorithm is an algorithm that calls a Python object to do the actual
 * work.
 * It defers the following methods to Python:
 * - ProcessRequest()
 *
 * Python signature of these methods is as follows:
 * - ProcessRequest(self, vtkself, request, inInfo, outInfo) : vtkself is the vtk object, inInfo is a tuple of information objects
 *
 * @sa
 * vtkPythonAlgorithm
*/

#ifndef VTKPYTHONCLASSALGORITHM_VTKPYTHONCLASSALGORITHM_H
#define VTKPYTHONCLASSALGORITHM_VTKPYTHONCLASSALGORITHM_H

#include "vtkPython.h" // Must be first

#include "vtkFiltersPythonModule.h" // For export macro
#include "vtkPythonAlgorithm.h"

#include <string>
#include <iostream>

class VTKFILTERSPYTHON_EXPORT vtkPythonClassAlgorithm : public vtkPythonAlgorithm {
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

  void SetDoubleProperty(const char* name, double value);
  void SetDoubleProperty(const char* name, double value1, double value2);
  void SetDoubleProperty(const char* name, double value1, double value2, double value3);

  void SetLongProperty(const char* name, long int value);
  void SetLongProperty(const char* name, long int value1, long int value2);
  void SetLongProperty(const char* name, long int value1, long int value2, long int value3);

protected:
  vtkPythonClassAlgorithm();
  ~vtkPythonClassAlgorithm();

  int ProcessRequest(vtkInformation* request,
                     vtkInformationVector** inInfo,
                     vtkInformationVector* outInfo) VTK_OVERRIDE;
  int FillInputPortInformation(int port, vtkInformation* info) VTK_OVERRIDE;
  int FillOutputPortInformation(int port, vtkInformation* info) VTK_OVERRIDE;

  //void UpdateProperties();
  void InstantiatePython();
  
private:
  vtkPythonClassAlgorithm(const vtkPythonClassAlgorithm&) VTK_DELETE_FUNCTION;
  void operator=(const vtkPythonClassAlgorithm&) VTK_DELETE_FUNCTION;
  
  PyObject* Module;
  PyObject* Object;
  //PyObject* PropertyDict;
  std::string ClassName;
  std::string ModuleName;
};

#endif // VTKPYTHONCLASSALGORITHM_VTKPYTHONCLASSALGORITHM_H

import sys
import traceback
from vtk import vtkDemandDrivenPipeline, vtkDataObject
from property import PvPythonPathProperty, assert_list

class PvAlgorithm(object):
    """
    Basic algorithm class. Defines 3 static attributes:
        - PythonPath: PvPythonPathProperty to specify additional paths added to sys.path (Note: The plugins's directory will be added by default)
        - InputClass: specify the input vtk types as either one type or a list of types. The number of elements will be used as number of input ports
        - OutputClass: see InputClass.
    The InputClass and OutputClass parameters have to be overwritten by the specialized classes or no input or output ports will be generated
    """
    PythonPath = PvPythonPathProperty()
    InputClass = None
    OutputClass = None
    def __init__(self):
        if self.InputClass is not None:
            self.num_inputs = len(assert_list(self.InputClass))
        else:
            self.num_inputs = 0

        if self.OutputClass is not None:
            self.num_outputs = len(assert_list(self.OutputClass))
        else:
            self.num_outputs = 0

    def FillOutputPortInformation(self, vtkself, port, info):
        return 1

    def FillInputPortInformation(self, vtkself, port, info):
        return 1

    def SetParameter(self, name, value):
        try:
            getattr(self, name)(value)
        except AttributeError as e:
            print(sys.exc_info())

    def GetParameter(self, name):
        try:
            return getattr(self, name)()
        except AttributeError as e:
            print(sys.exc_info())

    def SetParameterDict(self, prop):
        for k, v in prop.items():
            self.SetParameter(k, v)

    def Initialize(self, vtkself):
        return

    def ProcessRequest(self, vtkself, request, inputs, outputs):
        try:
            if request.Has(vtkDemandDrivenPipeline.REQUEST_DATA_OBJECT()):
                # print(request)
                if self.OutputClass is not None:
                    for i, c in assert_list(self.OutputClass):
                        dataobj = c()
                        outputs[i].GetInformationObject(0).Set(vtkDataObject.DATA_OBJECT(), dataobj)
                        vtkself.GetOutputPortInformation(1).Set(
                            vtkDataObject.DATA_EXTENT_TYPE(), dataobj.GetExtentType())
            if request.Has(vtkDemandDrivenPipeline.REQUEST_INFORMATION()):
                self.RequestInformation(vtkself, request, inputs, outputs)
            if request.Has(vtkDemandDrivenPipeline.REQUEST_DATA()):
                self.RequestData(vtkself, request, inputs, outputs)
        except:
            traceback.print_exc()

    def RequestInformation(self, vtkself, request, inputs, outputs):
        return

    def RequestData(self, vtkself, request, inputs, outputs):
        return

if __name__ == "__main__":

    class TestAlgorithm(PvAlgorithm):
        OutputClasses = vtkDataObject


    t = TestAlgorithm()

    print(t.OutputClasses)
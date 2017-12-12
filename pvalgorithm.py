import sys
import traceback
import json

from vtk import vtkDemandDrivenPipeline, vtkDataObject

class Algorithm(object):
    OutputDataClass = None
    def __init__(self):
        self.params = {}

    def FillOutputPortInformation(self, vtkself, port, info):
        return 1

    def FillInputPortInformation(self, vtkself, port, info):
        return 1

    def UpdateProperties(self, prop):
        print(prop)
        try:
            for kt in self.params.keys():
                try:
                    [k, t] = kt.split(':', 2)
                except ValueError:
                    [k, t] = [kt, 'json']
                if k in prop:
                    if isinstance(prop[k], (int, float)):
                        self.params[kt] = prop[k]
                    elif t == 'json':
                        self.params[kt] = json.loads(prop[k])
                    else:
                        self.params[kt] = prop[k]
        except:
            print(sys.exc_info())

    def Initialize(self, vtkself):
        return

    def ProcessRequest(self, vtkself, request, inputs, output):
        try:
            if request.Has(vtkDemandDrivenPipeline.REQUEST_DATA_OBJECT()):
                # print(request)
                if self.OutputDataClass is None:
                    try:
                        inobj = inputs[0].GetInformationObject(0).Get(
                            vtkDataObject.DATA_OBJECT())
                        dataobj = inobj.NewInstance()
                        self.OutputDataClass = dataobj.__class__
                    except AttributeError:
                        raise Exception('No OutputDataClass and no input data')
                else:
                    dataobj = self.OutputDataClass()
                output.GetInformationObject(0).Set(
                    vtkDataObject.DATA_OBJECT(), dataobj)
                vtkself.GetOutputPortInformation(0).Set(
                    vtkDataObject.DATA_EXTENT_TYPE(), dataobj.GetExtentType())
            if request.Has(vtkDemandDrivenPipeline.REQUEST_INFORMATION()):
                self.RequestInformation(vtkself, request, inputs, output)
            if request.Has(vtkDemandDrivenPipeline.REQUEST_DATA()):
                self.RequestData(vtkself, request, inputs, output)
        except:
            traceback.print_exc()

    def RequestInformation(self, vtkself, request, inputs, output):
        return

    def RequestData(self, vtkself, request, inputs, output):
        return

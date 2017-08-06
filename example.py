import sys
import json
import numpy as np

from vtk import vtkAlgorithm, vtkDemandDrivenPipeline
from vtk import vtkDataObject, vtkMultiBlockDataSet, vtkImageData
import paraview.vtk.numpy_interface.dataset_adapter as dsa
import paraview.util

class Algorithm(object):
    OutputDataClass = None
    def __init__(self):
        self.params = {}

    def FillOutputPortInformation(self, vtkself, port, info):
        return 1

    def FillInputPortInformation(self, vtkself, port, info):
        return 1

    def UpdateProperties(self, prop):
        try:
            for k in self.params.keys():
                if k in prop:
                    self.params[k] = json.loads(prop[k])
        except:
            print(sys.exc_info())

    def Initialize(self, vtkself):
        return

    def ProcessRequest(self, vtkself, request, inputs, output):
        try:
            if request.Has(vtkDemandDrivenPipeline.REQUEST_DATA_OBJECT()):
                if self.OutputDataClass is None:
                    inobj = inputs[0].GetInformationObject(0).Get(
                        vtkDataObject.DATA_OBJECT())
                    try:
                        dataobj = inobj.NewInstance()
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
            print(sys.exc_info())

    def RequestInformation(self, vtkself, request, inputs, output):
        return

    def RequestData(self, vtkself, request, inputs, output):
        return

class SinSource(Algorithm):
    OutputDataClass = vtkImageData
    def __init__(self):
        self.params = { 't0': 0.0, 't1': 1.0, 'f': 1.0, 'fs': 10.0 }

    def RequestInformation(self, vtkself, request, inputs, output):
        params = self.params
        N = int((params['t1'] - params['t0']) * params['fs'])
        paraview.util.SetOutputWholeExtent(vtkself, (0, N, 0, 0, 0, 0))

    def RequestData(self, vtkself, request, inputs, output):
        params = self.params
        N = int((params['t1'] - params['t0']) * params['fs'])
        vtkdata = output.GetInformationObject(0).Get(vtkDataObject.DATA_OBJECT())
        t = np.arange(params['t0'], params['t1'], 1.0/params['fs'])
        x = np.sin(2*np.pi*params['f']*t)
        data = dsa.WrapDataObject(vtkdata)
        vtkdata.SetDimensions((x.size, 1, 1))
        vtkdata.SetOrigin((params['t0'], 0, 0))
        vtkdata.SetSpacing(1/params['fs'], 0, 0)
        data.PointData.append(x, 'sin')

class MultiBlockSource(Algorithm):
    DataObjectClass = vtkMultiBlockDataSet
    def __init__(self):
        self.params = { 't0': 0.0, 't1': 1.0, 'f': 1.0, 'fs': 10.0, 'blocks': 2 }

    def generateSinData(self, vtkdata, s):
        params = self.params
        t = np.arange(params['t0'], params['t1'], 1.0/params['fs'])
        print('t: {}'.format(t))
        x = np.sin(2*np.pi*params['f']*t)
        data = dsa.WrapDataObject(vtkdata)
        vtkdata.SetDimensions((x.size, 1, 1))
        vtkdata.SetOrigin((params['t0'], 0, 0))
        vtkdata.SetSpacing(1/params['fs'], 0, 0)
        data.PointData.append(x*s, 'sin')
        data.PointData.append(t, 't')
    
    def RequestInformation(self, vtkself, request, inputs, output):
        params = self.params
        N = int((params['t1'] - params['t0']) * params['fs'])
        paraview.util.SetOutputWholeExtent(vtkself, (0, N, 0, 0, 0, 0))

    def RequestData(self, vtkself, request, inputs, output):
        mbds = output.GetInformationObject(0).Get(vtkDataObject.DATA_OBJECT())
        for i in range(0, self.params['blocks']):
            vtkdata = vtkImageData()
            self.generateSinData(vtkdata, i+1.0)
            mbds.SetBlock(i, vtkdata)

class MulFilter(Algorithm):
    OutputDataClass = vtkImageData

    def __init__(self):
        self.params = { "a": 2 }

    def RequestData(self, vtkself, request, inputs, output):
        vtkin = vtkImageData.GetData(inputs[0])
        vtkout = vtkImageData.GetData(output)
        vtkout.CopyStructure(vtkin)
        indata = dsa.WrapDataObject(vtkin)
        outdata = dsa.WrapDataObject(vtkout)
        for k in indata.PointData.keys():
            arr = indata.PointData[k]
            arr *= self.params['a']
            outdata.PointData.append(arr, "{}*{}".format(k, self.params['a']))

import numpy as np
import vtk
#import h5py
#import numpy_support
#import sklearn.neighbors
#import paraview.util
#import paraview.vtk.numpy_interface.dataset_adapter as dsa

import importlib

import pvalgorithm
importlib.reload(pvalgorithm)

class Table2Image(pvalgorithm.Algorithm):
    # OutputDataClass = vtk.vtkImageData
    OutputDataClass = vtk.vtkMultiBlockDataSet
    def RequestData(self, vtkself, request, inputs, output):
        outobj = self.OutputDataClass.GetData(output)
        image = vtk.vtkImageData()
        outobj.SetBlock(0, image)
        outobj.GetMetaData(0).Set(vtk.vtkCompositeDataSet.NAME(), "ImageData")
        inobj = vtk.vtkTable.GetData(inputs[0])
        rows = inobj.GetNumberOfRows()
        image.SetDimensions((rows, 1, 1))
        cols = inobj.GetNumberOfColumns()
        for i in range(0, cols):
            # vtkarr = inobj.GetColumn(i)
            # print(f"{vtkarr.GetName()}: {vtkarr.GetNumberOfTuples()}")
            image.GetPointData().AddArray(inobj.GetColumn(i))
        

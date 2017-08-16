import numpy as np
import vtk
import h5py
import paraview.util
import paraview.vtk.numpy_interface.dataset_adapter as dsa

import importlib

import pvalgorithm
importlib.reload(pvalgorithm)

class HDF5Reader(pvalgorithm.Algorithm):
    OutputDataClass = vtk.vtkMultiBlockDataSet
    def __init__(self):
        self.params = { 'FileName:string': '' }
        self.h5fh = None

    def RequestInformation(self, vtkself, request, inputs, output):
#        print(self.params)
        if self.h5fh is None:
            if self.params['FileName:string'] != '':
                self.h5fh = h5py.File(self.params['FileName:string'], 'r')

    def h5_to_mbds(self, group, mbds):
        def shape_3d(shape):
            if len(shape) == 3:
                return shape
            elif len(shape) == 2:
                return (1,) + shape
            elif len(shape) == 1:
                return (1, 1) + shape
            else:
                return (0, 0, 0)
#        mbds = vtk.MultiBlockDataSet()
        for (i, k) in enumerate(group):
            obj = group[k]
#            print(obj)
            if isinstance(obj, h5py.Group):
                child_mbds = vtk.vtkMultiBlockDataSet()
                self.h5_to_mbds(obj, child_mbds)
                mbds.SetBlock(i, child_mbds)
                mbds.GetMetaData(i).Set(vtk.vtkCompositeDataSet.NAME(), k)
            elif isinstance(obj, h5py.Dataset):
                vtkdata = vtk.vtkImageData()
                shape = tuple(reversed(shape_3d(obj.shape)))
#                print(shape)
                vtkdata.SetDimensions(shape)
                data = dsa.WrapDataObject(vtkdata)
                arr = obj[:].flatten()
#                print(arr)
                data.PointData.append(arr, k)
                mbds.SetBlock(i, vtkdata)
                mbds.GetMetaData(i).Set(vtk.vtkCompositeDataSet.NAME(), k)

    def RequestData(self, vtkself, request, inputs, output):
        mbds = self.OutputDataClass.GetData(output)
        self.h5_to_mbds(self.h5fh, mbds)
#        self.h5fh = None # Force reload


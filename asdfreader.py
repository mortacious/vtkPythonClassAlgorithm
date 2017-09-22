import numpy as np
import vtk
import asdf
import vtkndarray

import paraview.vtk.numpy_interface.dataset_adapter as dsa

import importlib

import pvalgorithm
importlib.reload(pvalgorithm)

class ASDFReader(pvalgorithm.Algorithm):
    OutputDataClass = vtk.vtkMultiBlockDataSet
    def __init__(self):
        self.params = { 'FileName:string': '' }
        self.fh = None

    def RequestInformation(self, vtkself, request, inputs, output):
#        print(self.params)
        if self.fh is None and self.params['FileName:string'] != '':
            self.fh = asdf.AsdfFile.open(self.params['FileName:string'], 'r')

    def asdf_to_mbds(self, tree, mbds):
        def shape_3d(shape):
            if len(shape) == 3:
                return shape
            elif len(shape) == 2:
                return (1,) + shape
            elif len(shape) == 1:
                return (1, 1) + shape
            else:
                return (1, 1, np.prod(shape))
#        mbds = vtk.MultiBlockDataSet()
        for (i, k) in enumerate(tree):
            obj = tree[k]
#            print(obj)
            if isinstance(obj, dict):
                child_mbds = vtk.vtkMultiBlockDataSet()
                self.asdf_to_mbds(obj, child_mbds)
                mbds.SetBlock(i, child_mbds)
                mbds.GetMetaData(i).Set(vtk.vtkCompositeDataSet.NAME(), k)
            elif hasattr(obj, 'shape'):
                vtkdata = vtk.vtkImageData()
                dim = tuple(reversed(shape_3d(obj.shape[0:-1])))
                arr = obj[:]
                arr.shape = (np.prod(dim), arr.shape[-1])
                vtkdata.SetDimensions(dim)
                data = dsa.WrapDataObject(vtkdata)
                data.PointData.append(arr, k)
                mbds.SetBlock(i, vtkdata)
                mbds.GetMetaData(i).Set(vtk.vtkCompositeDataSet.NAME(), k)

    def RequestData(self, vtkself, request, inputs, output):
        if self.fh is None and self.params['FileName:string'] != '':
            self.fh = asdf.AsdfFile.open(self.params['FileName:string'], 'r')
        if self.fh is not None:
            mbds = self.OutputDataClass.GetData(output)
            self.asdf_to_mbds(self.fh.tree, mbds)
#        self.h5fh = None # Force reload


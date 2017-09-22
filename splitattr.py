import numpy as np
import vtk

import importlib

import pvalgorithm
importlib.reload(pvalgorithm)

import vtkndarray
importlib.reload(vtkndarray)
from vtkndarray import vtkndarray, vtkarray_from_numpy

import mbdstree

class AttributeSplitter(pvalgorithm.Algorithm):
    outputDataClass = vtk.vtkMultiBlockDataSet
    def __init__(self):
        self.params = { 'attribute:string': None, 'format:string': '{attr}({groupkey}={g})' }

    def splitdatatree(self, img):
        data = img.data
        groupkey = self.params['attribute:string']
        groupidx = data.pop(groupkey)
        groups = np.unique(groupidx)
        blocks = {f'{groupkey}={g}': mbdstree.Image({attr: data[attr][groupidx == g][np.newaxis, np.newaxis, :, np.newaxis] for attr in data})
                  for g in groups}
        return blocks

    def splitdataflat(self, img):
        data = img.data
        groupkey = self.params['attribute:string']
        groupidx = data.pop(groupkey)
        groups = np.unique(groupidx)
        fmt = self.params['format:string']
        img = mbdstree.Image({fmt.format(attr=attr,g=g,groupkey=groupkey): data[attr][groupidx == g][np.newaxis, np.newaxis, :, np.newaxis] for attr in data for g in groups})
        return img
    
    def RequestData(self, vtkself, request, inputs, output):
        in_mbds = vtk.vtkMultiBlockDataSet.GetData(inputs[0])
        if in_mbds is None:
            in_mbds = vtk.vtkMultiBlockDataSet()
            in_mbds.SetBlock(0, vtk.vtkImageData.GetData(inputs[0]))
            in_mbds.GetMetaData(0).Set(vtk.vtkCompositeDataSet.NAME(), "ImageData")
        out_mbds = self.OutputDataClass.GetData(output)
        out_mbds.ShallowCopy(mbdstree.map_mbds(self.splitdatatree, in_mbds))
        # for i in range(0, in_mbds.GetNumberOfBlocks()):
        #     out_mbds.SetBlock(i, self.splitdata(in_mbds.GetBlock(i)))
        #     name = in_mbds.GetMetaData(i).Get(vtk.vtkCompositeDataSet.NAME())
        #     if name is not None:
        #         out_mbds.GetMetaData(i).Set(vtk.vtkCompositeDataSet.NAME(), name)

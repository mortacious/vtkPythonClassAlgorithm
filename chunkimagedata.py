import numpy as np
import vtk
import vtknumpy as vtknp
import mbdstree

import importlib

import pvalgorithm
importlib.reload(pvalgorithm)
importlib.reload(vtknp)
importlib.reload(mbdstree)

class ImageDataChunker(pvalgorithm.Algorithm):
    OutputDataClass = vtk.vtkMultiBlockDataSet
    def __init__(self):
        self.params = {'splits': []}

    def chunkimage(self, img):
        splits = self.params['splits']
        r = {}
        for k, arr in img.data.items():
            arrs = np.split(arr, splits, axis=-1)
            for (i, a) in enumerate(arrs):
                r[f'{k} ({i})'] = a
                # print(a.shape)
        return mbdstree.Image(r)
    
    def RequestData(self, vtkself, request, inputs, output):
        in_mbds = self.OutputDataClass.GetData(inputs[0])
        out_mbds = self.OutputDataClass.GetData(output)
        out_mbds.ShallowCopy(mbdstree.map_mbds(self.chunkimage, in_mbds))

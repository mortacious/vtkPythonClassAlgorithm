import numpy as np
import vtk
#import h5py
import vtknumpy as vtknp
import mbdstree
# import numpy_support
# import paraview.util
# import paraview.vtk.numpy_interface.dataset_adapter as dsa

import importlib

import pvalgorithm
importlib.reload(pvalgorithm)
importlib.reload(vtknp)
importlib.reload(mbdstree)

class ImageDataSplitter(pvalgorithm.Algorithm):
    OutputDataClass = vtk.vtkMultiBlockDataSet
    def __init__(self):
        self.params = {'format:string': '{k}({i},{j})'}
    def splitimagetree(self, img):
        return {f'z={i}':
                {f'y={j}': mbdstree.Image(
                    {f'{k}({i},{j})': v[i, j, :, :][np.newaxis, np.newaxis, :]
                     for k,v in img.data.items()})
                 for j in range(0, img.shape[1])}
                for i in range(0, img.shape[0])}

    def splitimage(self, img):
        fmt = self.params['format:string']
        return mbdstree.Image(
            {fmt.format(k=k,i=i,j=j): v[i, j, :, :][np.newaxis, np.newaxis, :]
             for k,v in img.data.items()
             for j in range(0, img.shape[1])
             for i in range(0, img.shape[0])})
    
    def RequestData(self, vtkself, request, inputs, output):
        in_mbds = self.OutputDataClass.GetData(inputs[0])
        out_mbds = self.OutputDataClass.GetData(output)
        out_mbds.ShallowCopy(mbdstree.map_mbds(self.splitimage, in_mbds))

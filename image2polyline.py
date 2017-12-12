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

class Image2PolyLine(pvalgorithm.Algorithm):
    OutputDataClass = vtk.vtkMultiBlockDataSet
    def __init__(self):
        self.params = { 'offset': 0, 'count': -1 }
    def image2poly(self, img):
        if not isinstance(img, mbdstree.Image):
            return {}
        def polyiter(img):
            for k, v in img.data.items():
                print(k)
                s = v.shape
                if (s[0], s[1], s[3]) == (1, 1, 3):
                    start = self.params['offset']
                    if self.params['count'] == -1:
                        end = s[2]
                    else:
                        end = start + self.params['count']
                    points = v[0, 0, start:end, :]
                    t = np.linspace(0, 1, points.shape[0])[:, np.newaxis]
                    yield (k, mbdstree.PolyLine(points, {'t': t}))
        r = {k: v for (k, v) in polyiter(img)}
        # print(r)
        return r
    
    def RequestData(self, vtkself, request, inputs, output):
        in_mbds = self.OutputDataClass.GetData(inputs[0])
        out_mbds = self.OutputDataClass.GetData(output)
        out_mbds.ShallowCopy(mbdstree.map_mbds(self.image2poly, in_mbds))

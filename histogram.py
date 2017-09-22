import collections
import numpy as np
import vtk
#import h5py
# import numpy_support
import sklearn.neighbors
# import paraview.util
# import paraview.vtk.numpy_interface.dataset_adapter as dsa

import importlib

import pvalgorithm
importlib.reload(pvalgorithm)

import vtkndarray
importlib.reload(vtkndarray)
from vtkndarray import vtkndarray, vtkarray_from_numpy

Image = collections.namedtuple('Image', ['data'])
def mbds_to_tree(mbds):
    r = {}
    for i in range(0, mbds.GetNumberOfBlocks()):
        block = mbds.GetBlock(i)
        name = mbds.GetMetaData(i).Get(vtk.vtkCompositeDataSet.NAME())
        if isinstance(block, vtk.vtkMultiBlockDataSet):
            r[name] = mbds_to_tree(block)
        elif isinstance(block, vtk.vtkImageData):
            rdim = tuple(reversed(block.GetDimensions()))
            vtkdata = block.GetPointData()
            vtkarrays = (vtkdata.GetAbstractArray(i)
                         for i in range(0, vtkdata.GetNumberOfArrays()))
            data = Image({arr.GetName(): vtkndarray(arr, shape=rdim + (arr.GetNumberOfComponents(),)) for arr in vtkarrays})
            r[name] = data
    return r

def tree_to_mbds(tree):
    mbds = vtk.vtkMultiBlockDataSet()
    for (i, (k, v)) in enumerate(tree.items()):
        if isinstance(v, Image):
            blockimage = vtk.vtkImageData()
            blockdata = blockimage.GetPointData()
            for (name, arr) in v.data.items():
                blockimage.SetDimensions(tuple(reversed(arr.shape[0:-1])))
                vtkarr = vtkarray_from_numpy(arr, vector=True)
                vtkarr.SetName(name)
                blockdata.AddArray(vtkarr)
            mbds.SetBlock(i, blockimage)
        else:
            mbds.SetBlock(i, tree_to_mbds(v))
        mbds.GetMetaData(i).Set(vtk.vtkCompositeDataSet.NAME(), k)
    return mbds

def map_tree(fn, tree):
    r = {k: map_tree(fn, v) if isinstance(v, dict) else fn(v)
         for (k, v) in tree.items()}
    return r

def map_pointdata(fn, mbds):
    tree = mbds_to_tree(mbds)
#    print(tree)
    r = map_tree(lambda img: Image({f'{fn.__name__}({k})': fn(v) for k, v in img.data.items()}),
                 tree)
    return tree_to_mbds(r)

def map_pointdata_along_axis(fn, mbds, axis=1):
    tree = mbds_to_tree(mbds)
    def mapper(img):
        print(next(iter(img.data.values())).shape)
        return Image({f'{fn.__name__}({k})': np.apply_along_axis(fn, axis, arr)
                      for k, arr in img.data.items()})
    r = map_tree(mapper, tree)
    return tree_to_mbds(r)

class KernelDensity(pvalgorithm.Algorithm):
    OutputDataClass = vtk.vtkMultiBlockDataSet
    
    def __init__(self):
        self.params = { 'kernel': 'gaussian', 'bandwidth': 1.0,
                        'range': [-1, 1], 'N': 10 }

    def kde(self, arr):
        kde = sklearn.neighbors.KernelDensity(kernel=self.params['kernel'],
                                              bandwidth=self.params['bandwidth'])
        arr.shape = (np.prod(arr.shape[0:-1]), arr.shape[-1])
        # arr[np.isnan(arr)] = 0
        # print(arr)
        kde.fit(arr)
        x = np.linspace(self.params['range'][0], self.params['range'][1],
                        self.params['N'])[:, np.newaxis]
        y = np.exp(kde.score_samples(x))
        # print(y)
        return y

    def kde2(self, arr):
        kde = sklearn.neighbors.KernelDensity(kernel=self.params['kernel'],
                                              bandwidth=self.params['bandwidth'])
        d = arr.shape[-1]
        zyx = arr.shape[0:-1]
        arr.shape = (np.prod(zyx, d))
        t = np.tile(np.arange(0, zyx[2]), zyx[1])
        t.shape = (t.size, 1)
        x = np.hstack(arr, t)
        kde.fit(x)

        (r0, r1) = self.params['range']
        N = self.params['N']
        tt, yy = np.meshgrid(t, np.linspace(r0, r1, N))

        x = np.hstack(tt.flatten(), yy.flatten())
        y = np.exp(kde.score_samples(x))
        y.shape = tt.shape + (1,)
        # print(y)
        return y
    
    def RequestData(self, vtkself, request, inputs, output):
        # print('RequestData', request)
        outobj = self.OutputDataClass.GetData(output)
        inobj = self.OutputDataClass.GetData(inputs[0])
        # inobj = inputs[0].GetInformationObject(0).Get(vtk.vtkDataObject.DATA_OBJECT())
        # r = vtk.vtkImageData()
        # # r = outobj
        # r.SetExtent((0, 9, 0, 0, 0, 0))
        # data = dsa.WrapDataObject(r).PointData
        # data.append(np.linspace(0, 1, 10), 'bla')
        # outobj.SetBlock(0, r)
        r = map_pointdata_along_axis(self.kde, inobj, 1)
        outobj.ShallowCopy(r)

class KernelDensity2(pvalgorithm.Algorithm):
    OutputDataClass = vtk.vtkMultiBlockDataSet
    
    def __init__(self):
        self.params = { 'kernel': 'gaussian', 'bandwidth': 1.0,
                        'range': [-1, 1], 'N': [20, 20] }

    def kde2(self, arr):
        kde = sklearn.neighbors.KernelDensity(kernel=self.params['kernel'],
                                              bandwidth=self.params['bandwidth'])
        d = arr.shape[-1]
        zyx = arr.shape[0:-1]
        arr.shape = (np.prod(zyx), d)
        t = np.tile(np.arange(0, zyx[2]), zyx[1])
        t.shape = (t.size, 1)
        x = np.hstack([t, arr])
        kde.fit(x)

        (r0, r1) = self.params['range']
        N = self.params['N']
        tt, yy = np.meshgrid(np.linspace(0, zyx[2], N[0]), np.linspace(r0, r1, N[1]))

        shape = tt.shape
        tt.shape = (tt.size, 1)
        yy.shape = (yy.size, 1)
        x = np.hstack([tt, yy])
        # print(x)
        y = np.exp(kde.score_samples(x))
        # y = tt
        y.shape = (1,) + shape + (1,)
        # print(y)
        print(y.shape)
        return y
    
    def RequestData(self, vtkself, request, inputs, output):
        outobj = self.OutputDataClass.GetData(output)
        inobj = self.OutputDataClass.GetData(inputs[0])
        r = map_pointdata(self.kde2, inobj)
        # print(r)
        outobj.ShallowCopy(r)

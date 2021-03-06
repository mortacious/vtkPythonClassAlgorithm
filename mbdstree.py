import collections
import numpy as np
import vtk
import vtknumpy as vtknp

class Image(object):
    def __init__(self, data, shape=None):
        self.data = data
        self.shape = shape if shape is not None else next(iter(data.values())).shape

PolyLine = collections.namedtuple('PolyLine', ['points', 'data'])
# Image = collections.namedtuple('Image', ['data'])
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
            data = Image({arr.GetName(): vtknp.vtk_to_numpy(arr, shape=rdim + (arr.GetNumberOfComponents(),)) for arr in vtkarrays})
            r[name] = data
    return r

def tree_to_mbds(tree):
    mbds = vtk.vtkMultiBlockDataSet()
    for (i, (k, v)) in enumerate((k, v) for k, v in tree.items() if v and v != {}):
        if isinstance(v, Image):
            blockimage = vtk.vtkImageData()
            blockdata = blockimage.GetPointData()
            for (name, arr) in v.data.items():
                blockimage.SetDimensions(tuple(reversed(arr.shape[0:-1])))
                vtkarr = vtknp.numpy_to_vtk(arr)
                vtkarr.SetName(name)
                blockdata.AddArray(vtkarr)
            mbds.SetBlock(i, blockimage)
        elif isinstance(v, PolyLine):
            poly = vtk.vtkPolyLine()
            pids = poly.GetPointIds()
            pids.SetNumberOfIds(v.points.shape[0])
            for j in range(0, v.points.shape[0]):
                pids.SetId(j, j)
            vtkpoints = vtk.vtkPoints()
            vtkpoints.SetData(vtknp.numpy_to_vtk(v.points))
            # print(vtkpoints)
            data = vtk.vtkPolyData()
            data.SetPoints(vtkpoints)
            data.Allocate(1, 1)
            data.InsertNextCell(poly.GetCellType(), pids)
            if v.data:
                pdata = data.GetPointData()
                # print(v.data)
                for (name, arr) in v.data.items():
                    vtkarr = vtknp.numpy_to_vtk(arr)
                    vtkarr.SetName(name)
                    pdata.AddArray(vtkarr)
            mbds.SetBlock(i, data)
        else:
            mbds.SetBlock(i, tree_to_mbds(v))
        mbds.GetMetaData(i).Set(vtk.vtkCompositeDataSet.NAME(), k)
    return mbds

def map_tree(fn, tree):
    r = {k: map_tree(fn, v) if isinstance(v, dict) else fn(v)
         for (k, v) in tree.items()}
    return r

def map_mbds(fn, mbds):
    tree = map_tree(fn, mbds_to_tree(mbds))
    # print(f'tree: {tree}')
    return tree_to_mbds(tree)

def map_pointdata(fn, mbds):
    tree = mbds_to_tree(mbds)
#    print(tree)
    r = map_tree(lambda img: Image({f'{fn.__name__}({k})': fn(v) for k, v in img.data.items()}),
                 tree)
    return tree_to_mbds(r)

def map_pointdata_along_axis(fn, mbds, axis=1):
    tree = mbds_to_tree(mbds)
    def mapper(img):
        # print(next(iter(img.data.values())).shape)
        return Image({f'{fn.__name__}({k})': np.apply_along_axis(fn, axis, arr)
                      for k, arr in img.data.items()})
    r = map_tree(mapper, tree)
    return tree_to_mbds(r)

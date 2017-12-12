from __future__ import division, absolute_import, print_function

import numpy as np        
import numpy
import vtk

__all__ = ['vtkndarray', 'fromvtk', 'vtkarray_from_numpy', 'array2vtk', 'numpy_to_vtk', 'vtk_to_numpy']

def get_numpy_array_type(vtk_array_type):
    """Returns a numpy array typecode given a VTK array type."""
    VTK_ID_TYPE_SIZE = vtk.vtkIdTypeArray().GetDataTypeSize()
    if VTK_ID_TYPE_SIZE == 4:
        ID_TYPE_CODE = numpy.int32
    elif VTK_ID_TYPE_SIZE == 8:
        ID_TYPE_CODE = numpy.int64
    VTK_LONG_TYPE_SIZE = vtk.vtkLongArray().GetDataTypeSize()
    if VTK_LONG_TYPE_SIZE == 4:
        LONG_TYPE_CODE = numpy.int32
        ULONG_TYPE_CODE = numpy.uint32
    elif VTK_LONG_TYPE_SIZE == 8:
        LONG_TYPE_CODE = numpy.int64
        ULONG_TYPE_CODE = numpy.uint64

    _vtk_np = {vtk.VTK_BIT:numpy.bool,
               vtk.VTK_CHAR:numpy.int8,
               vtk.VTK_SIGNED_CHAR:numpy.int8,
               vtk.VTK_UNSIGNED_CHAR:numpy.uint8,
               vtk.VTK_SHORT:numpy.int16,
               vtk.VTK_UNSIGNED_SHORT:numpy.uint16,
               vtk.VTK_INT:numpy.int32,
               vtk.VTK_UNSIGNED_INT:numpy.uint32,
               vtk.VTK_LONG:LONG_TYPE_CODE,
               vtk.VTK_LONG_LONG:numpy.int64,
               vtk.VTK_UNSIGNED_LONG:ULONG_TYPE_CODE,
               vtk.VTK_UNSIGNED_LONG_LONG:numpy.uint64,
               vtk.VTK_ID_TYPE:ID_TYPE_CODE,
               vtk.VTK_FLOAT:numpy.float32,
               vtk.VTK_DOUBLE:numpy.float64}
    return _vtk_np[vtk_array_type]

class vtkndarray(np.ndarray):
    """ """

    def __new__(subtype, vtkarray, shape=None, order='C'):
        dtype = get_numpy_array_type(vtkarray.GetDataType())
        if shape is None:
            shape = (vtkarray.GetNumberOfTuples(),
                     vtkarray.GetNumberOfComponents())

        self = np.ndarray.__new__(subtype, shape, dtype=dtype, buffer=vtkarray,
                                  order=order)
        self._vtkarray = vtkarray
        # self._vtkobj = vtk.vtkObject()
        # self._vtkarray.Register(self._vtkobj)
        return self

    # def __del__(self):
    #     if self._vtkarray is not None:
    #         # self._vtkarray.Unregister(self._vtkobj)
    #         # self._vtkobj = None
    #         self._vtkarray = None

    def __array_finalize__(self, obj):
        self._vtkarray = None
        # self._vtkobj = None

    def __array_wrap__(self, arr, context=None):
        arr = super(vtkndarray, self).__array_wrap__(arr, context)
        if self is arr or type(self) is not vtkndarray:
            return arr
        return arr.view(np.ndarray)

    def __getitem__(self, index):
        res = super(vtkndarray, self).__getitem__(index)
        if type(res) is vtkndarray and res._vtkarray is None:
            return res.view(type=np.ndarray)
        return res

def fromvtk(vtkarr, **kwargs):
    return vtkndarray(vtkarr, **kwargs)

vtk_to_numpy = fromvtk

def get_vtk_array_type(numpy_array_type):
    """Returns a VTK typecode given a numpy array."""
    # This is a Mapping from numpy array types to VTK array types.
    _np_vtk = {numpy.character:vtk.VTK_UNSIGNED_CHAR,
               numpy.uint8:vtk.VTK_UNSIGNED_CHAR,
               numpy.uint16:vtk.VTK_UNSIGNED_SHORT,
               numpy.uint32:vtk.VTK_UNSIGNED_INT,
               numpy.uint64:vtk.VTK_UNSIGNED_LONG_LONG,
               numpy.int8:vtk.VTK_CHAR,
               numpy.int16:vtk.VTK_SHORT,
               numpy.int32:vtk.VTK_INT,
               numpy.int64:vtk.VTK_LONG_LONG,
               numpy.float32:vtk.VTK_FLOAT,
               numpy.float64:vtk.VTK_DOUBLE,
               numpy.complex64:vtk.VTK_FLOAT,
               numpy.complex128:vtk.VTK_DOUBLE}
    for key, vtk_type in _np_vtk.items():
        if numpy_array_type == key or \
           numpy.issubdtype(numpy_array_type, key) or \
           numpy_array_type == numpy.dtype(key):
            return vtk_type
    raise TypeError(
        'Could not find a suitable VTK type for %s' % (str(numpy_array_type)))

def _MakeObserver(numpy_array):
    "Internal function used to attach a numpy array to a vtk array"
    def Closure(caller, event):
        foo = numpy_array
    return Closure

def numpy_to_vtk(nparray):
    """Converts a contiguous real numpy Array to a VTK array object."""

    nparray = np.ascontiguousarray(nparray)
    # print(nparray.flags)
    assert isinstance(nparray, np.ndarray) and nparray.flags.c_contiguous, 'Only C style contiguous arrays are supported.'

    vtktype = get_vtk_array_type(nparray.dtype)
    vtkarray = vtk.vtkDataArray.CreateDataArray(vtktype)
    vtkarray.SetVoidArray(nparray.data, nparray.size, 1)

    tuples = np.prod(nparray.shape[0:-1])
    components = nparray.shape[-1]
    vtkarray.SetNumberOfComponents(nparray.shape[-1])
    vtkarray.SetNumberOfTuples(np.prod(nparray.shape[0:-1]))
    
    vtkarray.AddObserver('DeleteEvent', _MakeObserver(nparray))
    return vtkarray

array2vtk = numpy_to_vtk
vtkarray_from_numpy = numpy_to_vtk

import math
import sqlite3
import itertools
import numpy as np
import vtk

import importlib

import pvalgorithm
importlib.reload(pvalgorithm)

import vtknumpy
importlib.reload(vtknumpy)

import mbdstree

# class SqlFilter_old(pvalgorithm.Algorithm):
#     # OutputDataClass = vtk.vtkImageData
#     OutputDataClass = vtk.vtkTable
#     def __init__(self):
#         print("FOOBLA")
#         self.params = { "query:string": "select * from data" }

#     def RequestData(self, vtkself, request, inputs, output):
#         print(1)
#         outobj = self.OutputDataClass.GetData(output)
#         result = outobj
#         # outobj.SetBlock(0, result)
#         intable = vtk.vtkTable.GetData(inputs[0])
#         data = intable.GetRowData()
#         colnames = [data.GetArrayName(i)
#                     for i in range(0, data.GetNumberOfArrays())]
#         arrays = [vtkndarray(data.GetArray(i))
#                   for i in range(0, data.GetNumberOfArrays())]
#         def rowiter(arr, n):
#             for i in range(0, n):
#                 r = tuple(float(a[i,0]) for a in arr)
#                 print(r)
#                 yield r
#         conn = sqlite3.connect(':memory:')
#         conn.create_function('log', -1, math.log)
#         curr = conn.cursor()
#         curr.execute(f'create table data ({",".join(colnames)})')
#         curr.executemany(f'insert into data values ({",".join("?" for _ in colnames)})', rowiter(arrays, data.GetNumberOfTuples()))
#         curr.execute(self.params['query:string'])
#         rcolnames = [x[0] for x in curr.description]
#         valiter = itertools.chain.from_iterable(curr)
#         rarr = np.fromiter(valiter, np.float)
#         rarr.shape = (int(rarr.size / len(rcolnames)), len(rcolnames))
#         rdata = result.GetRowData()
#         for (i,name) in enumerate(rcolnames):
#             colarr = np.ascontiguousarray(rarr[:, i])
#             vtkarr = vtkarray_from_numpy(colarr[:, np.newaxis])
#             vtkarr.SetName(name)
#             rdata.AddArray(vtkarr)

class SQLFilter(pvalgorithm.Algorithm):
    # OutputDataClass = vtk.vtkImageData
    OutputDataClass = vtk.vtkMultiBlockDataSet
    def __init__(self):
        print("FOOBLA")
        self.params = { "query:string": "select * from data" }

    def execute_sql(self, img):
        data = img.data
        colnames = list(data.keys())
        arrays = list(data.values())
        def rowiter(arr, n):
            for i in range(0, n):
                r = tuple(float(a.flatten()[i]) for a in arr)
                # print(r)
                yield r
        conn = sqlite3.connect(':memory:')
        conn.create_function('log', -1, math.log)
        curr = conn.cursor()
        curr.execute(f'create table data ({",".join(colnames)})')
        curr.executemany(f'insert into data values ({",".join("?" for _ in colnames)})', rowiter(arrays, np.prod(img.shape)))
        curr.execute(self.params['query:string'])
        rcolnames = [x[0] for x in curr.description]
        valiter = itertools.chain.from_iterable(curr)
        rarr = np.fromiter(valiter, np.float)
        rarr.shape = (int(rarr.size / len(rcolnames)), len(rcolnames))
        return mbdstree.Image({name: rarr[:, i][np.newaxis, np.newaxis, :, np.newaxis] for (i,name) in enumerate(rcolnames)})
        
    def RequestData(self, vtkself, request, inputs, output):
        in_mbds = vtk.vtkMultiBlockDataSet.GetData(inputs[0])
        if in_mbds is None:
            in_mbds = vtk.vtkMultiBlockDataSet()
            in_mbds.SetBlock(0, vtk.vtkImageData.GetData(inputs[0]))
            in_mbds.GetMetaData(0).Set(vtk.vtkCompositeDataSet.NAME(), "ImageData")
        out_mbds = self.OutputDataClass.GetData(output)
        out_mbds.ShallowCopy(mbdstree.map_mbds(self.execute_sql, in_mbds))

        # print(1)
        # outobj = self.OutputDataClass.GetData(output)
        
        # result = outobj
        # # outobj.SetBlock(0, result)
        # intable = vtk.vtkTable.GetData(inputs[0])
        # data = intable.GetRowData()
        # colnames = [data.GetArrayName(i)
        #             for i in range(0, data.GetNumberOfArrays())]
        # arrays = [vtkndarray(data.GetArray(i))
        #           for i in range(0, data.GetNumberOfArrays())]
        # def rowiter(arr, n):
        #     for i in range(0, n):
        #         r = tuple(float(a[i,0]) for a in arr)
        #         print(r)
        #         yield r
        # conn = sqlite3.connect(':memory:')
        # conn.create_function('log', -1, math.log)
        # curr = conn.cursor()
        # curr.execute(f'create table data ({",".join(colnames)})')
        # curr.executemany(f'insert into data values ({",".join("?" for _ in colnames)})', rowiter(arrays, data.GetNumberOfTuples()))
        # curr.execute(self.params['query:string'])
        # rcolnames = [x[0] for x in curr.description]
        # valiter = itertools.chain.from_iterable(curr)
        # rarr = np.fromiter(valiter, np.float)
        # rarr.shape = (int(rarr.size / len(rcolnames)), len(rcolnames))
        # rdata = result.GetRowData()
        # for (i,name) in enumerate(rcolnames):
        #     colarr = np.ascontiguousarray(rarr[:, i])
        #     vtkarr = vtkarray_from_numpy(colarr[:, np.newaxis])
        #     vtkarr.SetName(name)
        #     rdata.AddArray(vtkarr)
    

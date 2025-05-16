# This file is part of SHELVIS.
#
# Copyright 2024 SHELVIS developers
#
# Use of this source code is governed by a BSD-style license 
# that can be found in the LICENSE.md file.

"""VTK utilities
"""

import dataclasses
import numpy as np
import vtkmodules.util.numpy_support as vtk_numpy_support


@dataclasses.dataclass
class VertexData:
    data : np.ndarray
    scale : float = 1.0

    @property
    def x(self):
        return self.scale*self.data.T[0]

    @property
    def y(self):
        return self.scale*self.data.T[1]

    @property
    def z(self):
        return self.scale*self.data.T[2]


@dataclasses.dataclass
class ConnectivityData:
    data : np.ndarray

    @property
    def offsets(self):
        return self.data.reshape(-1, 4).T[0]

    @property
    def connectivity(self):
        return self.data.reshape(-1, 4)[:, 1:4].T
        
    @property
    def i(self):
        return self.connectivity[0]

    @property
    def j(self):
        return self.connectivity[1]

    @property
    def k(self):
        return self.connectivity[2]


class PolyData:

    @staticmethod
    def vertices(data, **kwargs):
        return VertexData(vtk_numpy_support.vtk_to_numpy(data.GetPoints().GetData()), 
                          scale=kwargs.get('scale', 1.0))

    @staticmethod
    def indices(data):
        return ConnectivityData(vtk_numpy_support.vtk_to_numpy(data.GetPolys().GetData()))
    
    @staticmethod
    def scalar_cell_data(data, name):
        
        s = vtk_numpy_support.vtk_to_numpy(data.GetCellData().GetArray(name))
        
        if len(s.shape) > 1:
            raise ValueError("Expected scalar data, got multiple components")

        return s

    @staticmethod
    def _get_data(data, name):
    
        # Get data assuming it is of cell data type
        cdata = data.GetCellData().GetArray(name)

        # Get data assuming it is of point data type
        pdata = data.GetPointData().GetArray(name)

        if (cdata is None) and (pdata is None):
            raise ValueError("Array not found in data")
    
        if pdata is not None:
            return pdata
        else:
            return cdata

    @staticmethod
    def scalar_point_data(data, name):
        
        s = vtk_numpy_support.vtk_to_numpy(data.GetPointData().GetArray(name))
        
        if len(s.shape) > 1:
            raise ValueError("Expected scalar data, got multiple components")

        return s

    @staticmethod
    def scalar(data, name):
                
        s = vtk_numpy_support.vtk_to_numpy(PolyData._get_data(data, name))
        
        if len(s.shape) > 1:
            raise ValueError("Expected scalar data, got multiple components")

        return s
    
    @staticmethod
    def vector(data, name):
        v = vtk_numpy_support.vtk_to_numpy(data.GetPointData().GetArray(name))
    
        return v
# This file is part of SHELVIS.
#
# Copyright 2024 SHELVIS developers
#
# Use of this source code is governed by a BSD-style license 
# that can be found in the LICENSE.md file.

"""Base class for datasets
"""

import numpy as np
import astropy.units

from shelvis.vtk.util import as_vtk_array


class DatasetBase:
    """A dataset that contains a coordinate frame and units for the data members.

    Assumes that DatasetBase is used via inheritance with an appropriate vtk object. 
    """
    
    def __init__(self, coordinate_frame):
        
        # The coordinate frame of the data
        self._coordinate_frame = coordinate_frame

        # Container that stores the unit of each data variable
        self._unit_of = dict()

    def unit(self, name):
        return self._unit_of[name]
    
    @property
    def coordinate_frame(self):
        return self._coordinate_frame
    
    def add_scalar(self, data, name, unit):
        """Add a scalar field to the dataset
        
        Note: A deep copy of the data is made so original data can be released
        """
        
        if (self.cells is None) or (self.points is None):
            raise ValueError("VTK object appears to be uninitialized.")


        # Input unit
        _unit = astropy.units.Unit(unit)
        
        # Convert to SI that is used internally by shelvis
        _array = data*_unit.si.scale
        
        if _array.size == self.cells.number_of_cells:
            _vtkdata = self.cell_data
        elif _array.size == self.points.number_of_points:
            _vtkdata = self.point_data
        else:
            raise ValueError("Array size not compatible as cell or point array.")
    
        # Add the array
        _vtkdata.AddArray(as_vtk_array(_array.flatten(order='F'),
                                       name=name, 
                                       deep_copy=True))

        # Register the unit of the data
        self._unit_of[name] = _unit.si.bases[0]

    def add_vector(self, data, name, unit):
        """Add a vector field to the dataset
        
        Note: A deep copy of the data is made so original data can be released
        """

        # Cartesian components of the vector field
        vx, vy, vz = data

        if not (vx.size == vy.size == vz.size):
            raise ValueError("Vector components should all be of equal size.")

        # Input unit
        _unit = astropy.units.Unit(unit)
        
        # Convert to SI that is used internally by shelvis
        vx *= _unit.si.scale
        vy *= _unit.si.scale
        vz *= _unit.si.scale
    
        vector_field \
            = np.array([vx.flatten(order='F'),
                        vy.flatten(order='F'),
                        vz.flatten(order='F')]).T

        vtk_vector_field = as_vtk_array(vector_field, name, deep_copy=True)

        if vx.size == self.cells.number_of_cells:
            _vtkdata = self.cell_data
        elif vx.size == self.points.number_of_points:
            _vtkdata = self.point_data
        else:
            raise ValueError("Array size not compatible as cell or point array.")
    
        _vtkdata.AddArray(vtk_vector_field)

        # Register the unit of this variable
        self._unit_of[name] = _unit.si.bases[0]
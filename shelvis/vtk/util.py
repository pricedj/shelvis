# This file is part of SHELVIS.
#
# Copyright 2024 SHELVIS developers
#
# Use of this source code is governed by a BSD-style license 
# that can be found in the LICENSE.md file.

"""VTK utilities
"""

import numpy as np
import numpy.typing

from vtkmodules.vtkCommonCore import vtkDataArray
from vtkmodules.vtkCommonCore import vtkPoints
from vtkmodules.util.numpy_support import numpy_to_vtk
from vtkmodules.util.numpy_support import vtk_to_numpy


def as_vtk_array(arr : numpy.typing.ArrayLike,
                 name : str = None,
                 deep_copy : bool = True) -> vtkDataArray:
    """Creates a VTK-compatible array from a given NumPy array. 

    Arguments
    ---------
    arr : ArrayLike
        The input array to convert.

    name : str, default: None
        The name of the array visible in VTK

    deep_copy : bool, default: True
        Whether to create a deep copy of the data. If True (default), the 
        data is copied and owned by the VTK object. If False, a shallow 
        reference is created and the original array must remain in scope.
     
    Returns
    -------
    vtk_arr : vtk.vtkDataArray
        A VTK-compatible data array.
    """

    if not isinstance(arr, np.ndarray):
        msg = f'Unsupported input array type ({type(arr)}).'
        raise TypeError(msg)
    
    # Ensure that the data is contiguous
    if not arr.flags.contiguous:
        arr = np.ascontiguousarray(arr)

    # Ensure that the data is little-endian
    if arr.dtype.byteorder == '>':
        arr = arr.byteswap(inplace=True)

    # Convert
    vtk_arr = numpy_to_vtk(num_array=arr, deep=deep_copy, array_type=None)

    # Set the name, if given
    if isinstance(name, str):
        vtk_arr.name = name
    
    return vtk_arr


def as_npy_array(arr : vtkDataArray) -> np.ndarray:
    """Creates a NumPy array from a VTK array.
    
    Arguments
    ---------
    arr : vtkDataArray
        The input VTK array to convert.
     
    Returns
    -------
    npy_arr : np.ndarray
        A NumPy array.
    """

    if not isinstance(arr, vtkDataArray):
        msg = f'Unsupported input array type ({type(arr)}).'
        raise TypeError(msg)
    
    return vtk_to_numpy(arr)


def as_vtk_points(arr : numpy.typing.ArrayLike, 
                  deep_copy : bool = True) -> vtkPoints:
    """Creates a VTK 3D points object from a given NumPy array. 

    Arguments
    ---------
    arr : ArrayLike
        The input coordintes to use as input. 

    deep_copy : bool, default: True
        Whether to create a deep copy of the data. If True (default), the 
        data is copied and owned by the VTK object. If False, a shallow 
        reference is created and the original array must remain in scope.
    
    Returns
    -------
    vtk_pts : vtk.vtkPoints
        A vtkPoint object.
    """

    # Get array as a vtk array
    arr = as_vtk_array(arr, deep_copy=deep_copy)

    # Create point object
    vtk_pts = vtkPoints()

    # Convert
    vtk_pts.data = numpy_to_vtk(num_array=arr, deep=deep_copy)

    return vtk_pts

# This file is part of SHELVIS.
#
# Copyright 2024 SHELVIS developers
#
# Use of this source code is governed by a BSD-style license 
# that can be found in the LICENSE.md file.

"""Utilities for importing CIDER output
"""

import numpy as np
import astropy.coordinates
import astropy.units as u

from vtkmodules.vtkCommonDataModel import vtkStructuredGrid

from shelvis.io.dataset import DatasetBase
from shelvis.vtk.util import as_vtk_points


class Dataset(DatasetBase, vtkStructuredGrid):
    """Importing a CIDER field
    """
    
    def __init__(self, coordinate_frame):
        
        DatasetBase.__init__(self, coordinate_frame=coordinate_frame)
        vtkStructuredGrid.__init__(self) 

    def _get_coords(self, mesh, frame):

        x1, x2, x3 = np.meshgrid(*mesh.edges, indexing="ij")

        # UGH!
        coords \
            = astropy.coordinates.SkyCoord(radius=x1.flatten(order='F')*u.m,
                                           lat=(0.5*np.pi - x2.flatten(order='F'))*u.rad,
                                           lon=x3.flatten(order='F')*u.rad,
                                           frame=frame)

        return coords
    
    def _get_cartesian_vector(self, field):
    
        r, th, ph = np.meshgrid(field.mesh.edges[0],
                                field.mesh.edges[1], 
                                field.mesh.edges[2],                            
                                indexing="ij")

        vr, vt, vp = field.data

        vx = vr*np.sin(th)*np.cos(ph) + vt*np.cos(th)*np.cos(ph) - vp*np.sin(ph)
        vy = vr*np.sin(th)*np.sin(ph) + vt*np.cos(th)*np.sin(ph) + vp*np.cos(ph)
        vz = vr*np.cos(th) - vt*np.sin(th)

        return vx, vy, vz

    def get_transformed_vector(self, field, frame):
        
        # Coordinates of the grid in the original system
        crds_old_frame = self._get_coords(field.mesh, frame)

        # Coordinate of the grid in the transformed system
        crds_new_frame = crds_old_frame.transform_to(self.coordinate_frame)

        # Vec in cartesian basis in original frame
        vx, vy, vz = self._get_cartesian_vector(field)

        # Field magnitude
        vabs = np.sqrt(vx*vx + vy*vy + vz*vz)

        # Unit vector components
        _vx = vx/vabs
        _vy = vy/vabs
        _vz = vz/vabs

        # Components of unit vector as SkyCoords
        _v = astropy.coordinates.SkyCoord(
                astropy.coordinates.CartesianRepresentation(_vx,
                                                            _vy,
                                                            _vz,
                                                             unit=u.m),
                frame=frame)

        # Transform
        _w = _v.transform_to(self.coordinate_frame)

        # Components in the new frame
        wx, wy, wz = vabs*_w.cartesian.get_xyz()

        return wx, wy, wz

    def add_vector(self, field, name, unit, frame):

        # First, transform the vector
        data = self.get_transformed_vector(field, frame)

        # Add the transformed vector
        DatasetBase.add_vector(self, data, name, unit)
        
    def from_field(self, field, frame):
        """Initialize the grid using a pysmsh field object instance

        Parameters
        ----------
        field : pysmsh Field
            The field object that contains the mesh
        frame : astropy coordinate frame
            The coordinate frame that `field` is defined in
        """

        # Get coordinates of the mesh as SkyCoords
        coords = self._get_coords(field.mesh, frame)

        # Transform coordinates to the intended frame
        coords = coords.transform_to(self.coordinate_frame)

        # Coordinates are internally stored in SI and in the Cartesian basis
        x, y, z = coords.cartesian.get_xyz().si.value

        # Set dimensions
        self.dimensions \
            = field.mesh.num_cells + 1

        # Set grid coordinates
        self.points \
            = as_vtk_points(np.array((x, y, z)).T, deep_copy=True)
        
   
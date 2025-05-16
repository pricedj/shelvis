# This file is part of SHELVIS.
#
# Copyright 2024 SHELVIS developers
#
# Use of this source code is governed by a BSD-style license 
# that can be found in the LICENSE.md file.

"""Geometric primitives constructed using VTK
"""

from vtkmodules.vtkFiltersSources import vtkArcSource
from vtkmodules.vtkFiltersSources import vtkSphereSource
from vtkmodules.vtkFiltersSources import vtkRegularPolygonSource


def circle(radius, **kwargs):
    
    polygon = vtkRegularPolygonSource(
        radius=radius,
        number_of_sides=64,
        **kwargs
    )

    polygon.Update()

    return polygon.output


def sphere(radius, **kwargs):

    sphere = vtkSphereSource(
        radius=radius,
        phi_resolution=45,
        theta_resolution=90,
        **kwargs
        )
    
    sphere.Update()

    return sphere.output


def polar_arc(radius, normal, **kwargs):
    # Arc from pole to pole

    arc = vtkArcSource(normal=normal,
                       center=(0, 0, 0),
                       angle=180.0, 
                       resolution=60, 
                       polar_vector=(0, 0, radius), 
                       use_normal_and_angle=True,
                       **kwargs
                       )
    
    arc.Update()

    return arc.output
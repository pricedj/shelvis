# This file is part of SHELVIS.
#
# Copyright 2024 SHELVIS developers
#
# Use of this source code is governed by a BSD-style license 
# that can be found in the LICENSE.md file.

"""Plotting of grid curves
"""

import numpy as np

import plotly
import plotly.graph_objects

import shelvis.vtk.polydata
import shelvis.vtk.primitives


class SphereGrid:
    
    @staticmethod
    def create(radius, name='Grid', num_lon=12, color='#f0c800', **kwargs):

        traces = list()

        # Create longitude arcs        
        for angle in np.linspace(0.0, 360.0, num_lon, endpoint=False):

            normal=(-np.sin(angle*np.pi/180.0), np.cos(angle*np.pi/180.0), 0.0)

            # Create points on circle
            pts = shelvis.vtk.polydata.PolyData.vertices(shelvis.vtk.primitives.polar_arc(radius=radius, 
                                                                                          normal=normal))
            
            # Add end point to close the circle
            #pts.data = np.append(pts.data, pts.data[0]).reshape(-1, 3)

            # Create arc plot
            arc = plotly.graph_objects.Scatter3d(x=pts.x, y=pts.y, z=pts.z, 
                                                 legendgroup=name,
                                                 legendgrouptitle={'text': name},
                                                 showlegend=False,
                                                 name="lon = {:2.1f}".format(angle),
                                                 line=dict(color=color, width=kwargs.get("width", 4)),
                                                 mode="lines")

            traces.append(arc)

        # Create latitude circles
        for clt in np.linspace(15.0, 180.0-15.0, 11):

            # Circle parameters
            _rho = radius*np.sin(clt*np.pi/180.0)
            normal = (0.0, 0.0, 1.0), 
            center = (0.0, 0.0, radius*np.cos(clt*np.pi/180.0))

            # Create points on circle
            pts = shelvis.vtk.polydata.PolyData.vertices(shelvis.vtk.primitives.circle(_rho, 
                                                                                       normal=normal, 
                                                                                       center=center))
            
            # Add end point to close the circle
            pts.data = np.append(pts.data, pts.data[0]).reshape(-1, 3)

            # Create circle plot
            circle = plotly.graph_objects.Scatter3d(x=pts.x, y=pts.y, z=pts.z, 
                                                    legendgroup=name,
                                                    legendgrouptitle={'text': name},
                                                    showlegend=False,
                                                    name="lat = {:2.1f}".format(90.0 - clt),
                                                    line=dict(color=color, width=kwargs.get("width", 4)),
                                                    mode="lines")

            traces.append(circle)

        trace = plotly.graph_objects.Scatter3d(x=[radius, radius], y=[0, 0], z=[0, 0], 
                                                    legendgroup=name,
                                                    showlegend=True,
                                                    name=name,
                                                    line=dict(color=color, width=kwargs.get("width", 4)),
                                                    mode="lines",
                                                    visible=True
                                                    )
        traces.append(trace)
        
        return traces
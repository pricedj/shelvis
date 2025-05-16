# This file is part of SHELVIS.
#
# Copyright 2024 SHELVIS developers
#
# Use of this source code is governed by a BSD-style license 
# that can be found in the LICENSE.md file.

"""Rendering polygonal data using Plotly
"""

import astropy.units

import plotly
import plotly.graph_objects

import shelvis.vtk.polydata



class PolyDataPlot:

    @staticmethod
    def create_plot(polydata, name=None, unit=None, **kwargs):
        
        # Get data of the polygonal mesh
        vertices \
            = shelvis.vtk.polydata.PolyData.vertices(polydata, **kwargs)
        
        connectivity \
            = shelvis.vtk.polydata.PolyData.indices(polydata).connectivity
        
        # Default plot settings
        #settings = dict(lighting=dict(ambient=0.8, roughness=0.5, diffuse=0.8, fresnel=0.2, specular=0.05))
        settings = dict()

        if name is not None:
            
            if unit is None:
                unit = astropy.units.dimensionless_unscaled
                
            # Get values
            values \
                = shelvis.vtk.polydata.PolyData.scalar(polydata, name)

            # Scale from SI to the plot unit
            values *= 1.0/unit.si.scale

           
            settings["intensity"] = values

            if len(values) != len(vertices.x):
                settings["intensitymode"] = "cell"
            else:
                settings["intensitymode"] = "vertex"

            # Name of plot in trace menu
            settings["name"] = name.capitalize()
            
            # Default colormap
            settings["colorscale"] = "gray"

            # Default colorbar settings            
            colorbar_title = name
            if not unit.is_equivalent(astropy.units.dimensionless_unscaled):
                colorbar_title += " [{}] ".format(unit.to_string())

            settings["colorbar"] \
                = dict(orientation="v", len=0.5, xref='paper',
                       title=dict(text=colorbar_title))
                       #x=1.01, y=0.20, len=0.5, 
                       #title=dict(text=colorbar_title))

            settings["showlegend"] = True

        else:

            settings["color"] = 'gray'


        plot = plotly.graph_objects.Mesh3d(x=vertices.x, 
                                           y=vertices.y, 
                                           z=vertices.z, 
                                           i=connectivity[0], 
                                           j=connectivity[1], 
                                           k=connectivity[2],
                                           **settings) 
                        
        return plot

    @staticmethod
    def update(plot, polydata, name=None, unit=None, **kwargs):

        # New data
        vertices \
            = shelvis.vtk.polydata.PolyData.vertices(polydata, **kwargs)

        connectivity \
            = shelvis.vtk.polydata.PolyData.indices(polydata).connectivity
        
        # Update the polygonal mesh
        plot.x = vertices.x
        plot.y = vertices.y
        plot.z = vertices.z

        plot.i, plot.j, plot.k = connectivity

        # Update values
        if name is not None:

            values \
                = shelvis.vtk.polydata.PolyData.scalar(polydata, name)

            if unit is None:
                unit = astropy.units.dimensionless_unscaled
            
            plot.intensity = values/unit.si.scale

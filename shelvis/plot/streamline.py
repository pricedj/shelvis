# This file is part of SHELVIS.
#
# Copyright 2024 SHELVIS developers
#
# Use of this source code is governed by a BSD-style license 
# that can be found in the LICENSE.md file.

"""Streamline plot
"""

import shelvis
import shelvis.widgets.plot
import shelvis.vtk.tracer
import shelvis.core.containers
import plotly.graph_objects as go


class StreamlinePlot(shelvis.widgets.plot.PlotWidget):
    """A widget for plotting values on a surface extracted from 3D data.
    
    Parameters
    ----------
    data : 
        The object containing the mesh and data
    name: str
        Descriptive unique name for the plot
    variable: str
        The name of the vector field in `data` to trace
    """

    def __init__(self, data, name, variable):

        super().__init__(name=name)

        self._tracer = shelvis.vtk.tracer.StreamTracer(data, variable)

        self.seeds = shelvis.core.containers.SkyCoordContainer()

    @property
    def tracer(self):
        return self._tracer
    
    def _link_menu_items(self):
        self.seeds.observe(self._on_seeds_change, names='points')

    def _on_seeds_change(self, change):

        added, removed, updated = shelvis.core.containers.SkyCoordContainer.changes_to_points(change["old"], change["new"])
    
        _fig = self.plot.parent

        # Init new figure data
        new_fig_data = [d for d in _fig.data]

        # Plot names
        names = [d.name for d in _fig.data]

        # Remove plots that have been marked to be removed or updated.
        # Names of plots to be removed
        to_be_removed = set(list(removed) + list(updated))
    
        # Create new figure data list
        new_fig_data = [d for d in _fig.data if d.name not in to_be_removed]

        # Set new figure data
        _fig.data = new_fig_data
       
        # Redraw the plots that have been updated
        for key in list(updated):
            _fig.add_traces(self.trace_sources(key))
            
        # Add new plots
        for key in list(added):
            _fig.add_traces(self.trace_sources(key))
            
    def create_plot(self):
        
        # Create a dummy plot
        return go.Scatter3d(x=[0, 0], y=[0, 0], z=[0, 0], 
                            mode="lines", 
                            name="__dummy__", 
                            #legendgroup=label, 
                            showlegend=False,
                            visible=False
                            )

    def trace_sources(self, label):

        # Get the seed points to trace
        seed = self.seeds[label]

        # Trace one by one
        traces = list()

        scale_crds = (shelvis.internal.unit.length/self.unit_of_length).si.value

        if seed.isscalar:

            # Get coordinate scaled from internal unit (si) to plot unit
            x, y, z = self._tracer.trace(seed)*scale_crds
            
            traces.append(go.Scatter3d(x=x, y=y, z=z, 
                                       mode="lines", 
                                       name=label, 
                                       legendgroup=label, 
                                       showlegend=True))
    
        else:

            for s in seed:

                x, y, z = self._tracer.trace(s)*scale_crds
            
                traces.append(go.Scatter3d(x=x, y=y, z=z, 
                                           mode="lines", 
                                           name=label, 
                                           legendgroup=label, 
                                           showlegend=False))
            
        traces[0].showlegend = True
        traces[0].name = label
                
        return traces
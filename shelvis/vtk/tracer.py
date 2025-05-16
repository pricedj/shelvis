# This file is part of SHELVIS.
#
# Copyright 2024 SHELVIS developers
#
# Use of this source code is governed by a BSD-style license 
# that can be found in the LICENSE.md file.

"""VTK Streamline tracer
"""

import numpy as np

from shelvis import internal
import shelvis.vtk.util

from vtkmodules.vtkFiltersFlowPaths import vtkStreamTracer


class StreamTracer:
    """Streamline tracing using vtkStreamTracer

    Parameters
    ----------
    data : 
        The object containing the mesh and data
    variable: str
        The name of the vector field in `data` used in the tracing
    integration_direction : str, default: "both"
        Directions in which to trace. Either "both", "forward" or "backward"  
    """
    
    def __init__(self, data, variable, integration_direction="both"):
                
        self.tracer = vtkStreamTracer()

        # Build the bijective mapping between tracing direction string 
        # and the vtk integer
        self._integration_dir = dict()
        for direction in ("both", "forward", "backward"):
            value = getattr(self.tracer, direction.upper())
            self._integration_dir[direction] = value
            self._integration_dir[value] = direction
        
        # Set integration direction
        self.integration_direction = integration_direction

        # Store coordinate frame of the data
        self.coordinate_frame = data.coordinate_frame
        
        # Ugh!!!
        # TODO
        data.GetPointData().SetActiveVectors(variable)

        # Set the input data for the tracer
        self.tracer.input_data = data
        self.tracer.Update()
       
    @property
    def integration_direction(self):
       """Returns the string indicating the integration direction
       """
       return self._integration_dir[self.tracer.integration_direction]

    @integration_direction.setter
    def integration_direction(self, value):
        """Set the integration direction.
        
        Parameters
        ----------
        value : str, one of "both", "forward", "backward"
        """

        direction_str = value.strip().lower()
        
        if direction_str not in ("both", "forward", "backward"):
            raise ValueError(
                "Integration direction must be either 'backward', 'forward', or 'both' - not '{direction_str}'"
            )

        self.tracer.integration_direction = self._integration_dir[direction_str]

    @property
    def max_length(self):
        """Returns the maximum length that the streamline is traced
        """
        return self.tracer.maximum_propagation*internal.unit.length

    @max_length.setter
    def max_length(self, value):
        """Set the maximum length of the streamline

        Parameters
        ----------
        value : astropy.units.Quantity
        """
        self.tracer.maximum_propagation = value.to_value(internal.unit.length)

    @property
    def max_step(self):
        """Returns the maximum step that the tracer is allowed to take
        """
        return self.tracer.maximum_integration_step*internal.unit.length

    @max_step.setter
    def max_step(self, value):
        """Set the maximum step that the tracer is allowed to take

        Parameters
        ----------
        value : astropy.units.Quantity
        """
        self.tracer.maximum_integration_step = value.to_value(internal.unit.length)

    def _split_curve(self, curve):

        x, y, z = curve.T
        
        dsqr = x*x + y*y + z*z

        isect = np.where(np.isclose(dsqr, dsqr[0]))[0]
        
        curve1, curve2 = np.array_split(curve, np.delete(isect, 0))

        return np.concatenate((curve1[:0:-1], curve2))

    def trace_from_point(self, point):
        """Trace a streamline from a single seed point
        """

        # Transform the seed coordinate to this frame
        transformed_point = point.transform_to(self.coordinate_frame)
        
        # Set the seed position
        self.tracer.start_position = transformed_point.cartesian.get_xyz().to_value(internal.unit.length)

        # Trace
        self.tracer.Update()

        # Get the points of the curve
        curve = shelvis.vtk.util.as_npy_array(self.tracer.output.points.data)

        if self.integration_direction == "both":
            return self._split_curve(curve).T
        else:
            return curve.T
                
    def trace(self, seed):

        if seed.isscalar:
            return self.trace_from_point(seed)
        else:
            raise ValueError("Tracer expected a single point as the seed to trace from")
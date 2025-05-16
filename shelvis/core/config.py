# This file is part of SHELVIS.
#
# Copyright 2024 SHELVIS developers
#
# Use of this source code is governed by a BSD-style license 
# that can be found in the LICENSE.md file.

"""Default configuration definitions
"""

import dataclasses
import astropy.units

from .configparams import ConfigParams


class UnitConfig(ConfigParams):
    length: astropy.units.Quantity = 1*astropy.units.m


@dataclasses.dataclass
class Config:
    unit : UnitConfig = UnitConfig()
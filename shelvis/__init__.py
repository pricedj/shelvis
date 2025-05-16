

from .core.config import Config

# Internal configuration parameters of SHELVIS
internal = Config()

# import frequently used plots
from .plot.figure import Visualization 
from .plot.slice import SlicePlot
from .plot.isocontour import IsocontourPlot
from .plot.streamline import StreamlinePlot
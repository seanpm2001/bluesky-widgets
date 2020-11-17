from collections import namedtuple

from .utils.list import EventedList
from .utils.spec import define_spec


FigureSpec = define_spec("FigureSpec", ["axes_specs"])
"Describes a Figure"
# It is an intentional limitation that Figure must be given all its Axes at
# definition time. Axes cannot be added dynamically. This constraint could be
# relaxed in the future, at the cost of some added complexity.

AxesSpec = define_spec("AxesSpec", ["figure_spec", "x_label", "y_label"])
"Describes a set of Axes"

LineSpec = define_spec("LineSpec", ["func", "run", "axes_spec", "args", "kwargs"])
"Describes a line (both data and style)"


class FigureSpecList(EventedList):
    ...


class AxesSpecList(EventedList):
    ...


class LineSpecList(EventedList):
    ...


class GridSpecList(EventedList):
    ...


class ImageStackList(EventedList):
    ...


def is_complete(run):
    return run.metadata["stop"] is not None


def prompt_line_builder(run):
    """
    This is a simple example.

    This makes a hard-coded assumption that the data has columns "motor" and
    "det" in the primary stream.
    """

    def func(run):
        "Return any arrays x, y. They must be of equal length."
        # *Lazily* read the data so that large arrays are not loaded unless
        # the yare used.
        ds = run.primary.read()
        # Do any computation you want in here....
        return ds["motor"], ds["det"]

    axes_spec = AxesSpec("motor", "det")
    figure_spec = FigureSpec((axes_spec,))
    line_spec = LineSpec(func, run, axes_spec, (), {})

    return [figure_spec, axes_spec, line_spec]


class StreamingPlotBuilder:
    """
    Base class for streaming builders
    """

    def __init__(self):
        self.figures = FigureSpecList()
        self.axes = AxesSpecList()
        self.lines = LineSpecList()
        self.grids = GridSpecList()
        self.image_stacks = ImageStackList()
        ...

    def __call__(self, run):
        # Implement this in the subclass.
        ...


class LastNLines(StreamingPlotBuilder):
    """
    Plot y vs x for the last N runs.
    """

    def __init__(self, x, y, N, stream_name="primary"):
        # Stash these and expose them as read-only properties.
        self._N = N
        self._x = x
        self._y = y
        self._stream_name = stream_name
        self._current_axes = None
        super().__init__()

    def new_plot(self):
        "Create a fresh plot, leaving the previous one (if any) as is."
        axes_spec = AxesSpec(self.x, self.y)
        figure_spec = FigureSpec((axes_spec,))
        self.figures.append(figure_spec)
        self._current_axes = axes_spec

    def use_plot(self, axes_spec):
        "Use an existing plot."
        self._current_axes = axes_spec

    def add_line(self, run):
        # Create a new Figure and Axes if we do not already have one.
        if self._current_axes is None:
            self.new_plot()
        # If necessary, removes lines to make room for the new line.
        while len(self.lines) >= self.N:
            self.lines.pop()

        stream_name = self.stream_name
        x = self.x
        y = self.y

        def func(run):
            # *Lazily* read the data so that large arrays are not loaded unless
            # the yare used.
            ds = run[stream_name].to_dask()
            return ds[x], ds[y]

        line_spec = LineSpec(func, run, self._current_axes, (), {})

        self.lines.append(line_spec)

    def __call__(self, run):
        # If the stream of interest is defined already, plot now.
        if self.stream_name in run:
            self.add_line(run)
        # Otherwise, connect a callback to run when the stream of interest arrives.
        run.events.new_stream.connect(self.on_new_stream)
        run.events.completed.disconnect(self.on_new_stream)

    def on_new_stream(self, event):
        "This callback runs whenever BlueskyRun has a new stream."
        if event.name == self.stream_name:
            self.add_line(event.run)

    # Read-only properties so that these settings are inspectable, but not
    # changeable.

    @property
    def N(self):
        return self._N

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @property
    def stream_name(self):
        return self._stream_name
import random
import textwrap
from collections import namedtuple
from math import sqrt

import bokeh.io
import bokeh.plotting
import networkx as nx
from bokeh import models
from bokeh.colors import RGB


class BokehGraphColorMapException(Exception):
    hint = textwrap.dedent(
        """
        Ensure color_by and palette are set to valid attributes.

        Available palettes with up to 256 colors, are:
        ["cividis", "grey", "gray", "inferno", "magma", "viridis",
        "Greys256", "Inferno256", "Magma256", "Plasma256", "Viridis256", "Cividis256", "Turbo256"]
        All avalailabe palettes can be found here:
        https://docs.bokeh.org/en/latest/docs/reference/palettes.html

        For attributes with more than 256 categories, a colormap can be computed with
        BokehGraph.colormap(palette, color_by, steps)
        Maximum number of steps is 256.
        Or set palette to 'random'.
    """,
    )

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg + "\n" + self.hint


class BokehGraphColorMap:
    def __init__(self, palette, max_colors=-1):
        self.palette_name = palette

        if max_colors > 256:
            raise BokehGraphColorMapException("Maximum number of colors is 256 !")
        self.max_colors = max_colors
        self.anchors = None

    @staticmethod
    def _float_range(start, stop, step):
        while start < stop:
            yield start
            start += step

    @staticmethod
    def _color_map(categories, palette):
        return {group: color for group, color in zip(categories, palette)}

    @staticmethod
    def _map_dict_to_iterable(d, iterable):
        return [d[i] for i in iterable]

    def _reduce_categories(self, iterable, steps):
        min_val = min(iterable)
        max_val = max(iterable)
        step_size = (max_val - min_val) / steps
        self.anchors = list(self._float_range(min_val, max_val, step_size))
        new = []
        for val in iterable:
            best = min(self.anchors, key=lambda x: abs(x - val))
            new.append(best)
        return new

    @staticmethod
    def create_palette(palette_name, n_colors):
        if palette_name.endswith("256"):
            palette = bokeh.palettes.all_palettes[palette_name]
        elif palette_name == "random":
            palette = [
                RGB(random.randrange(0, 256), random.randrange(0, 256), random.randrange(0, 256))
                for _ in range(n_colors)
            ]
        elif palette_name in ["cividis", "grey", "gray", "inferno", "magma", "viridis"]:
            palette = getattr(bokeh.palettes, palette_name)(n_colors)
        else:
            try:
                if n_colors == 2:
                    # Use maximum contrast if only two colors
                    palette = bokeh.palettes.all_palettes[palette_name][3]
                    palette = [palette[0], palette[-1]]
                else:
                    palette = bokeh.palettes.all_palettes[palette_name][n_colors]
            except KeyError as e:
                raise BokehGraphColorMapException(
                    "Palette {} does not exist or support {} colors !".format(
                        palette_name,
                        n_colors,
                    ),
                ) from e
        return palette

    def map(self, color_attribute):

        categories = set(color_attribute)
        n_categories = len(categories)

        if self.max_colors > 0:
            if n_categories > self.max_colors:
                color_map_values = self._reduce_categories(color_attribute, self.max_colors)
                n_colors = len(set(color_map_values))
            else:
                n_colors = n_categories
                color_map_values = color_attribute
        elif n_categories < 257:
            n_colors = n_categories
            color_map_values = color_attribute
        else:
            raise BokehGraphColorMapException(
                (
                    "Too many categories color attribute! {}\n"
                    "Set max_colors to a value: 0 < max_colors <= 256 !".format(n_categories)
                ),
            )
        palette = self.create_palette(self.palette_name, n_colors)
        colormap = self._color_map(set(color_map_values), palette)
        return self._map_dict_to_iterable(colormap, color_map_values)


class BokehGraph(object):
    """
    This is instanciated with a (one-mode) networkx graph object with BokehGraph(nx.Graph())

    working example:
    import networkx as nx
    graph = nx.barbell_graph(5,6)
    degrees = nx.degree(graph)
    nx.set_node_attributes(graph, dict(degrees), "degree")
    plot = BokehGraph(graph, width=800, height=600, inline=True)
    plot.layout(shrink_factor = 0.6)
    plot.draw(color_by="degree", palette="Category20", max_colors=2)


    The plot is drawn by BokehGraph.draw(node_color="firebrick")
        - node_color, line_color can be set to every value that bokeh recognizes, including
          a bokeh.colors.RGB instance. serveral other parameters can be found in the .draw method.


    """

    def __init__(self, graph, width=800, height=600, inline=True):

        self.graph = graph

        self.width = width
        self.height = height

        self._layout = None
        self._nodes = None
        self._edges = None

        self.colormap = None

        self._hovertool = None
        self.figure = None
        self.node_attributes = sorted(
            {attr for _, data in self.graph.nodes(data=True) for attr in data},
        )
        self.node_properties = None
        self._tooltips = [("node", "@_node")]
        for attr in self.node_attributes:
            self._tooltips.append((attr, f"@{attr}"))

        # inline for jupyter notebooks
        if inline:
            bokeh.io.output_notebook(hide_banner=True)
            self.show = lambda x: bokeh.plotting.show(x, notebook_handle=True)

        else:
            self.show = lambda x: bokeh.plotting.show(x)

    def gen_edge_coordinates(self):
        if not self._layout:
            self.layout()

        xs = []
        ys = []
        val = namedtuple("edges", "xs ys")

        for edge in self.graph.edges():
            from_node = self._layout[edge[0]]
            to_node = self._layout[edge[1]]
            xs.append([from_node[0], to_node[0]])
            ys.append([from_node[1], to_node[1]])

        return val(xs=xs, ys=ys)

    def gen_node_coordinates(self):
        if not self._layout:
            self.layout()

        names, coords = zip(*self._layout.items())
        xs, ys = zip(*coords)
        val = namedtuple("nodes", "names xs ys")

        return val(names=names, xs=xs, ys=ys)

    def layout(self, layout=None, shrink_factor=0.8, iterations=50, scale=1):
        self._nodes = None
        self._edges = None
        if not layout:
            self._layout = nx.spring_layout(
                self.graph,
                k=1 / (sqrt(self.graph.number_of_nodes() * shrink_factor)),
                iterations=iterations,
                scale=scale,
            )
        else:
            self._layout = layout
        return

    def prepare_figure(self):
        formatter = {tip: "printf" for tip, _ in self._tooltips}
        hovertool = models.HoverTool(
            tooltips=self._tooltips,
            formatters=formatter,
            names=["show_hover"],
        )

        fig = bokeh.plotting.figure(
            width=self.width,
            height=self.height,
            tools=[hovertool, "box_zoom", "reset", "wheel_zoom", "pan"],
        )

        fig.toolbar.logo = None
        fig.axis.visible = False
        fig.xgrid.grid_line_color = None
        fig.ygrid.grid_line_color = None
        return fig

    def draw(
        self,
        node_color="firebrick",
        palette=None,
        color_by=None,
        line_color="navy",
        edge_alpha=0.17,
        node_alpha=0.7,
        node_size=9,
        max_colors=-1,
    ):

        if not self._nodes:
            self._nodes = self.gen_node_coordinates()
        if not self._edges:
            self._edges = self.gen_edge_coordinates()

        figure = self.prepare_figure()

        # Draw Edges
        source_edges = bokeh.models.ColumnDataSource(dict(xs=self._edges.xs, ys=self._edges.ys))
        figure.multi_line("xs", "ys", line_color=line_color, source=source_edges, alpha=edge_alpha)

        # Draw circles
        self.node_properties = dict(
            xs=self._nodes.xs,
            ys=self._nodes.ys,
            _node=self._nodes.names,
        )

        for attr in self.node_attributes:
            self.node_properties[attr] = [self.graph.nodes[n][attr] for n in self._nodes.names]

        if color_by and palette:
            self.colormap = BokehGraphColorMap(palette, max_colors)
            self.node_properties["_colormap"] = self.colormap.map(self.node_properties[color_by])
            color = "_colormap"
        else:
            color = node_color
        source_nodes = bokeh.models.ColumnDataSource(self.node_properties)

        figure.circle(
            "xs",
            "ys",
            fill_color=color,
            line_color=color,
            source=source_nodes,
            alpha=node_alpha,
            size=node_size,
            name="show_hover",
        )

        self.figure = figure
        self.show(self.figure)

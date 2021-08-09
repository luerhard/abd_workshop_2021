from collections import defaultdict, OrderedDict
from collections.abc import Mapping, Iterable

from asciitree import LeftAligned
from asciitree import drawing


class cdict(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.counterdict = defaultdict(int)

    def __setitem__(self, key, val):
        super().__setitem__(key, val)
        self.counterdict[key] += 1
        return val


class JSONTreeView:
    def __init__(self, max_depth=10, max_nodes=50, percentage=False, horiz_len=1, indent=2, style="BOX_ASCII"):
        """Create a tree object from JSON Data

        Keyword Arguments:
            max_depth {int} -- how deep into the branches the tree is supposed to be displayed (default: {10})
            max_nodes {int} -- how many items a single node is allowed to have (default: {50})
            percentage {bool} -- show percentage of total next to the numbers (default: {False})
            horiz_len {int} -- see documentation of asciitree (default: {1})
            indent {int} -- see documentation of asciitree (default: {2})
            style {str} -- possibilites are ['BOX_ASCII', 'BOX_DOUBLE', 'BOX_BLANK', 'BOX_HEAVY', 'BOX_LIGHT']
                            ; for details see documenation of asciitree (default: {"BOX_ASCII"})

            The documentation of asciitree can be found here: https://pythonhosted.org/asciitree/
        """
        self.percentage = percentage
        self.max_nodes = max_nodes
        self.max_depth = max_depth
        self.list_placeholder = "[LIST]"
        self.n = 0
        self.tree = cdict()
        self.count_tree = OrderedDict()
        _style = getattr(drawing, style)
        self.viewer = LeftAligned(draw=drawing.BoxStyle(gfx=_style, horiz_len=horiz_len, indent=indent))
        self._append_dots = []

    def show(self, data):
        """computes and prints the tree

        Arguments:
            data {Iterable[Mapping]} -- The data that is supposed to be summarized

        Returns:
            [asciitree.LeftAligned] -- raw text that results in a graph when printed
        """
        self.compute(data)
        self._parse_count(self.tree)
        for path in self._append_dots:
            self._walk_tree(self.count_tree, path)["..."] = dict()
        return self.viewer({f"Summary: (Total items: {self.n})": self.count_tree})

    def _n_label(self, n):
        if self.percentage:
            label = f"{n} ({round(n / self.n * 100, 2)}%)"
        else:
            label = f"{n}"
        return label

    def _parse_count(self, d, path=[]):

        for i, (key, val) in enumerate(sorted(d.items())):
            if key in self._walk_tree(self.count_tree, path):
                continue
            n = d.counterdict[key]
            k = f"{key} - {self._n_label(n)}"
            self._walk_tree(self.count_tree, path)[k] = OrderedDict()
            if i <= self.max_nodes:
                self._parse_count(val, path=path + [k])
            else:
                self._append_dots.append(path)
                return

    def compute(self, data):
        for d in data:
            self.n += 1
            self._parse(d)
        return self.tree

    @staticmethod
    def _walk_tree(tree, path):
        d = tree
        for p in path:
            d = d[p]
        return d

    def _parse(self, d, path=[]):
        if len(path) >= self.max_depth:
            return

        if isinstance(d, Mapping):
            for key, val in d.items():
                if key in self._walk_tree(self.tree, path):
                    self._walk_tree(self.tree, path).counterdict[key] += 1
                else:
                    self._walk_tree(self.tree, path)[key] = cdict()
                self._parse(val, path=path + [key])
        elif isinstance(d, Iterable) and not isinstance(d, str):
            if self.list_placeholder in self._walk_tree(self.tree, path):
                self._walk_tree(self.tree, path).counterdict[self.list_placeholder] += 1
            else:
                self._walk_tree(self.tree, path)[self.list_placeholder] = cdict()

            for item in d:
                self._parse(item, path=path + [self.list_placeholder])

class Graph(object):
    """
    >>> g = Graph(['oboe', 'flute'])
    >>> g.add('oboe', [{'duration': 4, 'pitch': 60}, {'duration': 4, 'pitch': 62}])
    >>> g.add('flute', [{'duration': 2, 'pitch': 64}, {'duration': 4, 'pitch': 67}, {'duration': 2, 'pitch': 67}])
    >>> g.get(



    """

    def __init__(self, ensemble):
        self._ensemble = ensemble
        self._by_instrument = {}
        self._by_beat = {}


        for item in self._list:
            item['music'] = []

            # Enable getting an instrument object as an attribute or by string
            # Example: ensemble.oboe or ensemble['oboe']
            variable_name = item.get('variable_name', item['name'])

            self.names.append(variable_name)
            self._dict[variable_name] = item
            setattr(self, variable_name, item)

        self.bass = ['piano_left', 'cello']
        self.treble = ['soprano', 'flute', 'oboe', 'piano_right', 'cello']

    def __iter__(self):
        for item in self._list:
            yield item

    def __getitem__(self, arg):
        if arg in range(len(self._list)):
            return self._list[arg]
        if arg in self._dict:
            return self._dict[arg]


class Graph(object):
    """

    >>> g = Graph()
    >>> g.add_instruments(['oboe', 'flute', 'guitar'])
    >>> g.instruments
    ['oboe', 'flute', 'guitar']
    >>> g.add_bars('all', [1, 2, 3, 4])
    >>> g.get_bars('oboe', 1, 3)
    [2, 3]
    >>> g.get_bars(['oboe', 'guitar'], 2)
    {'oboe': [3], 'guitar': [3]}


    """
    def __init__(self):
        self.graph = {}
        self.instruments = []

    def __repr__(self):
        return '<Graph {}>'.format(self.graph)

    def add_instruments(self, names):
        self.instruments.extend(names)
        for name in names:
            self.graph[name] = []

    def fill(self, n_bars=None):
        if not n_bars:
            n_bars = max([len(bars) for bars in self.graph.itervalues()])
        for i in self.graph:
            part = self.graph[i]
            remaining = n_bars - len(part)
            part.extend([None] * remaining)

    def add_bars(self, bars, instruments=None):
        if instruments is None:
            instruments = self.instruments
        if isinstance(instruments, basestring):
            instruments = [instruments]
        for i in instruments:
            self.graph[i].extend(bars)

    def get_bars(self, instruments=None, start=0, end=None):
        # TODO: Should this return a dict or a new Graph instance?
        # TODO: parse args
        if instruments is None:
            instruments = self.instruments
        if isinstance(instruments, basestring):
            instruments = [instruments]

        subgraph = {}
        for i in instruments:
            part = self.graph[i]
            if end is None:
                end = len(part)
            subgraph[i] = part[start:end]

        return subgraph

    def insert_bar(self, bar, index, instrument):
        self.graph[instrument][index] = bar










if __name__ == '__main__':
    import doctest
    doctest.testmod()

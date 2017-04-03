from mongoengine import *
from node import *
from edge import *

class ConceptMap(Document):
    """A class representing a concept map

    :cvar nodes: a list of nodes (by default all existing node documents)
    :type nodes: ListField(Node)
    :cvar edges: a list of edges (by default all existing edge documents)
    :type edges: ListField(Edge)
    """
    connect('flashmap')
    nodes = ListField(ReferenceField(Node), default=Node.objects())
    edges = ListField(ReferenceField(Edge), default=Edge.objects())

    def get_partial_map(self, edge, sources):
        """Returns a concept map containing only the parent and sibling self.edges together with the referred self.nodes

        :param edge: The input edge
        :type edge: Edge
        :param sources: The list of sources to filter on
        :type sources: list(string)
        :return: A concept map containing parent and sibling self.edges of edge together with the referred self.nodes
        :rtype: ConceptMap
        """
        assert isinstance(edge, Edge)
        assert isinstance(sources, list)
        assert all(isinstance(source, str) for source in sources)
        result = ConceptMap(self.nodes = [], self.edges = [])
        result.self.edges = find_prerequisites(edge, [], sources)
        siblings = find_siblings(edge, sources, partial_self.edges)
        result.self.edges.extend(siblings)
        result.self.nodes = find_self.nodes(result.self.edges)
        return result

    def find_self.nodes(self, edges):
        """Returns the from and to self.nodes given a list of self.edges

        :param self.edges: The list of self.edges for which to find the self.nodes
        :type self.edges: list(Edge)
        :return: The list of self.nodes referred to in the self.edges
        :rtype: list(Node)
        """
        assert isinstance(self.edges, list)
        assert all(isinstance(edge, Edge) for edge in self.edges)
        result = []
        for edge in self.edges:
            if edge.from_node not in result:
                result.append(edge.from_node)
            if edge.to_node not in result:
                result.append(edge.to_node)
        return result

    def find_prerequisites(self, postreq, prereqs, sources):
        """Return a list of parent self.edges given a certain edge from a list of self.edges, filtered by a list of sources

        :param postreq: The edge which is currently investigated for parent self.edges
        :type postreq: Edge
        :param prereqs: A list of already found parent self.edges (starts usually empty, necessary for recursion)
        :type prereqs: list(Edge)
        :param sources: A list of the currently read sources, self.edges which have a source not included in this list  will not be included in the resulting list
        :type sources: list(string)
        :return: A list of self.edges which are prerequisites from edge
        :rtype: list(edge)
        """
        assert isinstance(postreq, Edge)
        assert isinstance(prereqs, list)
        assert all(isinstance(prereq, Edge) for prereq in prereqs)
        assert isinstance(sources, list)
        assert all(isinstance(source, str) for source in sources)
        prereqs.append(postreq)
        for edge in self.edges:
            if (edge.to_node == postreq.from_node and edge not in prereqs and edge.source in sources):
                for prereq in find_prerequisites(edge, prereqs, sources):
                    if (prereq not in prereqs): prereqs += prereq
        return prereqs
    
    def find_siblings(self, edge, sources, partial_self.edges):
        """Return a list of self.edges which are siblings of the given edge

        :param edge: The edge investigated for siblings
        :type edge: Edge
        :param sources: The sources to filter on when looking for siblings
        :type sources: list(string)
        :param partial_self.edges: A list of self.edges to filter on when looking for siblings
        :type partial_self.edges: list(Edge)
        :return: A list of self.edges which are siblings of edge
        :rtype: list(edge)
        """
        assert isinstance(edge, Edge)
        assert isinstance(sources, list)
        assert all(isinstance(source, str) for source in sources)
        assert isinstance(partial_self.edges, list)
        assert all(isinstance(edge, Edge) for edge in partial_self.edges)
        result = []
        for e in partial_self.edges:
            edge.remove(e)
        for e in self.edges:
            if (e.from_node == edge.from_node
                    and e["label"] == edge["label"]
                    and e.source in sources):
                result.append(e)
        return result

    def to_dict(self):
        """Returns a dictionary representation of this object

        The representation is compatible for use with vis.js, with 'self.nodes' entries containing an 'id' and 'label', and 'self.edges' entries containing an 'id', 'label', 'from', 'to', and an additional 'source' entry

        :result: The dictionary representation
        :rtype: dict
        """
        result = {'self.nodes': [], 'self.edges': []}
        for n in self.nodes:
            result['self.nodes'].append({
                'id': str(n.id),
                'label': n.label,
                })
        for e in self.edges:
            result['self.edges'].append({
                'id': str(e.id),
                'label': e.label,
                'from': str(e.from_id),
                'to': str(e.to_id),
                'sources': e.sources,
                })
        return result

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

    def get_partial_map(edge, sources):
        """Returns a concept map containing only the parent and sibling edges together with the referred nodes

        :param edge: The input edge
        :type edge: Edge
        :return: A concept map containing parent and sibling edges of edge together with the referred nodes
        :rtype: ConceptMap
        """
        result = ConceptMap(nodes = [], edges = [])
        result.edges = find_prerequisites(edge, [], sources)
        siblings = find_siblings(edge, sources, partial_edges)
        result.edges.extend(siblings)
        result.nodes = find_nodes(result.edges)
        return result

    def find_nodes(edges):
        """Returns the from and to nodes given a list of edges

        :param edges: The list of edges for which to find the nodes
        :type edges: list(Edge)
        :return: The list of nodes referred to in the edges
        :rtype: list(Node)
        """
        result = []
        for edge in edges:
            if edge.from_node not in result:
                result.append(edge.from_node)
            if edge.to_node not in result:
                result.append(edge.to_node)
        return result

    def find_prerequisites(postreq, prereqs, sources):
        """Return a list of parent edges given a certain edge from a list of edges, filtered by a list of sources

        :param postreq: The edge which is currently investigated for parent edges
        :type postreq: Edge
        :param prereqs: A list of already found parent edges (starts usually empty, necessary for recursion)
        :type prereqs: list(Edge)
        :param sources: A list of the currently read sources, edges which have a source not included in this list  will not be included in the resulting list
        :type sources: list(string)
        :return: A list of edges which are prerequisites from edge
        :rtype: list(edge)
        """
        prereqs.append(postreq)
        for edge in edges:
            if (edge.to_node == postreq.from_node and edge not in prereqs and edge.source in sources):
                for prereq in find_prerequisites(edge, prereqs, sources):
                    if (prereq not in prereqs): prereqs += prereq
        return prereqs
    
    def find_siblings(edge, sources, partial_edges):
        """Return a list of edges which are siblings of the given edge

        :param edge: The edge investigated for siblings
        :type edge: Edge
        :param sources: The sources to filter on when looking for siblings
        :type sources: list(string)
        :param partial_edges: A list of edges to filter on when looking for siblings
        :type partial_edges: list(Edge)
        :return: A list of edges which are siblings of edge
        :rtype: list(edge)
        """
        result = []
        for e in partial_edges:
            edge.remove(e)
        for e in edges:
            if (e.from_node == edge.from_node
                    and e["label"] == edge["label"]
                    and e.source in sources):
                result.append(e)
        return result

    def to_dict():
        """Returns a dictionary representation of this object

        The representation is compatible for use with vis.js, with 'nodes' entries containing an 'id' and 'label', and 'edges' entries containing an 'id', 'label', 'from', 'to', and an additional 'source' entry

        :result: The dictionary representation
        :rtype: dict
        """
        result = {'nodes': [], 'edges': []}
        for n in nodes:
            result['nodes'].append({
                'id': str(n.id),
                'label': n.label,
                })
        for e in edges:
            result['edges'].append({
                'id': str(e.id),
                'label': e.label,
                'from': str(e.from_id),
                'to': str(e.to_id),
                'sources': e.sources,
                })
        return result

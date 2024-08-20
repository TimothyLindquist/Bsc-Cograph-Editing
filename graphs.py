# -*- coding: utf-8 -*-

import networkx as nx
from networkx import random_graphs as rg
from networkx import community as com
from tralda import cograph as co, supertree as st, datastructures as ds
import random as rand
from triples import triple_dict_to_list, triple_subset

__author__ = "Timothy Lindquist"

def comp_graph(R : dict, V : list or iter) -> nx.Graph:
    '''
    Constructs a weighted comparability graph with vertices V
    out of triples R.

    Parameters
    ----------
    R : dict
        Triples.
    V : iter
        Vertices/leaves.

    Returns
    -------
    A : nx.Graph
        Edge weighted comparability/Aho graph.

    '''
    A = nx.Graph()
    A.add_nodes_from(V)
    edges = [(x,y) for x,y in R if len(R[x,y]) > 0 and x in V and y in V]
    for x,y in edges:
        # Keep weights of leaves not in V
        A.add_edge(x, y, weight=len([x,y]))
    return A
    

def subgraph(G : nx.Graph, V : list or iter) -> nx.Graph:
    '''
    Constructs the induced subgraph of G on V.

    Parameters
    ----------
    G : nx.Graph
        
    V : iter
        Vertices.

    Returns
    -------
    Gnew : nx.Graph
        Non-shallow induced subgraph of G on V.

    '''
    
    tmp = G.subgraph(V)
    Gnew = nx.Graph()
    Gnew.add_nodes_from(tmp.nodes(data=True))
    Gnew.add_edges_from(tmp.edges(data=True))
    return Gnew

def edit_random_edges(G : nx.graph, n : int, add : bool = True) -> None:
    '''
    Edits n random edges of G.

    Parameters
    ----------
    G : nx.graph
        
    n : int
        Number of edges to edit.
    add : bool, optional
        False if edges should be removed. The default is True.

    Returns
    -------
    None.

    '''
    C = list(nx.connected_components(G))
    if add and len(C) > 1:
        for _ in range(n):
            c1,c2 = rand.sample(C,2)
            v1 = rand.choice(c1)
            v2 = rand.choice(c2)
            G.add_edge(v1,v2)
    else:
        v1,v2 = nx.approximation.randomized_partitioning(G)[1]
        for v in v1:
            for u in v2:
                if G.has_edge(v,u):
                    G.remove_edge(v,u)

def random_nograph(n : int, p=0.5):
    '''
    Constructs a random non-cograph on n vertices.

    Parameters
    ----------
    n : int
        Number of vertices.
    p : float, optional
        Edge probability in [0,1]. The default is 0.5.

    Returns
    -------
    nx.Graph
        Non cograph.

    '''
    if p < 0.1 or p > 0.9:
        raise ValueError("p must be in [0.1,0.9]")
    G = rg.fast_gnp_random_graph(n,p)
    if co.LinearCographDetector(G).recognition():
        return random_nograph(n,p)
    return G

def random_cograph(n : int) -> nx.Graph:
    '''
    Constructs a cograph on n vertices.

    Parameters
    ----------
    n : int
        Number of vertices.

    Returns
    -------
    nx.Graph
        Cograph.

    '''
    T = co.random_cotree(n)
    return co.to_cograph(T)

def disturbed_random_cograph(n : int, d : int) -> nx.Graph:
    """
    

    Parameters
    ----------
    n : int
        Number of vertices.
    d : int
        Number of disturbances.

    Returns
    -------
    nx.Graph
        Non-cograph on n vertices whose minimum cograph editing solution 
        is no larger than d.

    """
    cograph = True
    while cograph:
        T = co.random_cotree(n)
        G = co.to_cograph(T)
        edges = list(nx.complement(G).edges) +list(G.edges)
        rand.shuffle(edges)
        for _ in range(d):
            if edges != []:
                i = rand.randint(0, len(edges) - 1)
                x,y = edges.pop(i)
                if G.has_edge(x, y):
                    G.remove_edge(x, y)
                else:
                    G.add_edge(x,y)
        cograph = co.LinearCographDetector(G).recognition()
    return G

def path_graph(n : int, label_start=0) -> nx.Graph:
    '''
    Constructs a path graph on n vertices with optional user controlled 
    vertex labels.

    Parameters
    ----------
    n : int
        Number of vertices.
    label_start : int, optional
        The label of the first vertex. The default is 0.

    Returns
    -------
    G : nx.Graph
        Path graph.

    '''
    
    G = nx.Graph()
    for i in range(label_start, label_start + n-1):
        G.add_edge(i,i+1)
    return G

def union(G1 : nx.Graph, G2 : nx.Graph) -> nx.Graph:
    """
    Constructs the graph that is the union of G1 and G2.

    Parameters
    ----------
    G1 : nx.Graph

    G2 : nx.Graph

    Returns
    -------
    G : nx.Graph
        The union of G1 & G2.

    """
    
    G = G1.copy()
    G.add_nodes_from(G2.nodes)
    G.add_edges_from(G2.edges)
    return G

def join(G1 : nx.Graph, G2 : nx.Graph) -> nx.Graph:
    """
    Constructs the graph that is the join of G1 and G2.

    Parameters
    ----------
    G1 : nx.Graph

    G2 : nx.Graph

    Returns
    -------
    G : nx.Graph
        The join of G1 & G2.

    """
    G = union(G1,G2)
    G.add_edges_from([(x,y) for x in G1.nodes for y in G2.nodes])
    return G

def recursive_join(C) -> nx.Graph:
    """
    Used to construct

    Parameters
    ----------
    C : List
        Entries are components of a comparability graph.

    Returns
    -------
    G : nx.Graph
        A graph whose triples induce C.

    """
    G = nx.Graph()
    for c in C:
        if type(c) == list: 
            G = join(G,recursive_union(c))
        else:
            tmp = nx.Graph()
            tmp.add_node(c)
            G = join(G, tmp)
    return G

def recursive_union(C) -> nx.Graph:
    """
    

    Parameters
    ----------
    C : List
        Entries are compononents of a comparability graph.

    Returns
    -------
    G : nx.Graph
        A graph whose triples induce C.

    """
    G = nx.Graph()
    for c in C:
        if type(c) == list:
            G = union(G,recursive_join(c))
        else:
            tmp = nx.Graph()
            tmp.add_node(c)
            G = union(G, tmp)
    return G
    
def splinter(R : dict, L : list or iter, init : bool = True) -> list:
    """
    Uses BUILD to construct a list representation of the tree.

    Parameters
    ----------
    R : dict
        Triples.
    L : iter
        Leaves/vertices.

    Returns
    -------
    S : list
        A list representing a cotree (if one can be found)
        without inner node labels.
        
    References
    ----------
    Aho, Alfred V., et al. "Inferring a tree from lowest common ancestors with
    an application to the optimization of relational expressions."
    SIAM Journal on Computing 10.3 (1981): 405-421.

    """
    if init:
        r = triple_dict_to_list(R)
        if not st.Build(r, L).build_tree():
            
            raise RuntimeError("R is not consistent. There is no cograph.")
            return
    S = []
    G = nx.Graph()
    G.add_nodes_from(L)
    G.add_edges_from([(x,y) for x,y in R.keys()])
    C = list(nx.connected_components(G))
    for c in C:
        if len(c) == 1:
            S.extend(c)
        else:
            Rnew = {}
            for x,y in R.keys():
                if x in c and y in c:
                    for z in R[x,y]:
                        if z in c:
                            if (x,y) in Rnew.keys():
                                Rnew[x,y].append(z)
                            else:
                                Rnew[x,y] = [z]
            S.append(splinter(Rnew,c,False))
    return S

def triples_to_cograph(R : dict, L : list or iter, root=1):
    """
    Given a set of compatible triples, a graph in which all are present
    is computed.

    Parameters
    ----------
    R : List
        Entries should be triples.
    L : List
        Entries should be nodes/vertices/leaves.
    root : Any, optional
        If the original graph is disconnected, set to anything but 1.
        The default is 1.

    Returns
    -------
    G : nx.Graph
        Cograph.

    """
    
    S = splinter(R,L)
    G = nx.Graph()
    if root == 1:
        G = recursive_join(S)
    else:
        G = recursive_union(S)
    return G

def BUILD_cograph(R : dict, L : iter, label : int = 0) -> nx.Graph:
    """
    Uses BUILD to construct a cograph if one exists.

    Parameters
    ----------
    R : dict
        Triples.
    L : iter
        Leaves/vertices.
    label : int
        0 for disjoint union, 1 for join.

    Returns
    -------
    G : nx.Graph
        Cograph if it exists, otherwise none.
        
    References
    ----------
    Aho, Alfred V., et al. "Inferring a tree from lowest common ancestors with
    an application to the optimization of relational expressions."
    SIAM Journal on Computing 10.3 (1981): 405-421.

    """
    G = nx.Graph()
    if len(L) == 1:
        G.add_node(L[0])
        return G
    if len(L) == 2:
        G.add_nodes_from(L)
        if label == 1:
            G.add_edge(L[0],L[1])
        return G
    
    CG = comp_graph(R, L)
    comps = list(nx.connected_components(CG))
    if len(comps) == 1:
        raise Exception("R is not compatible.")
        return
    for C in comps:
        if label == 1:
            G=join(G,BUILD_cograph(
                triple_subset(R,C),list(C),0))
        else:
            G = union(G,BUILD_cograph(
                triple_subset(R,C),list(C),1))
    return G
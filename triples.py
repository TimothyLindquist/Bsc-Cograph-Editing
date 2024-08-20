# -*- coding: utf-8 -*-

import networkx as nx

__author__ = 'Timothy Lindquist'

def is_triple(G : nx.Graph, t : set, R1=True , R2=True) -> bool:
    '''
    

    Parameters
    ----------
    G : nx.Graph
        
    t : 3-set
        triple (x,y,z)
    R1 : bool, optional
        Include R1 satisfying triples. The default is True.
    R2 : R2, optional
        Include R2 satisfying triples. The default is True.

    Returns
    -------
    bool
        True if (x,y,z) is a triple in G under chosen restrictions.

    '''
    
    x,y,z = t
    
    # Check for triple satisfaction
    if not G.has_edge(y,z) and not G.has_edge(x,z):
    
        if R1:
            if G.has_edge(x,y):
                return True
        if R2 and not G.has_edge(x,y):
            for n in G.neighbors(x):
                if G.has_edge(y,n) and not G.has_edge(z,n):
                    return True
        return False
    
    if G.has_edge(x,z) and G.has_edge(y,z):
        
        if R1:
            if not G.has_edge(x,y):
                return True
        if R2 and G.has_edge(x,y):
            for n in G.neighbors(z):
                if not G.has_edge(x,n) and not G.has_edge(y,n):
                    return True
        return False
    return False

def get_triples(G : nx.Graph, R1=True, R2=True) -> dict:
    '''
    

    Parameters
    ----------
    G : nx.Graph
      
    R1 : bool, optional
        Include R1 satisfying triples. The default is True.
    R2 : R2, optional
        Include R2 satisfying triples. The default is True.

    Returns
    -------
    triples : dict
        key (x,y) with values [z,...] for every triple xy|*.

    '''
    
    V = list(G.nodes)
    triples = {}
    for i in range(len(V)-1):
        for j in range(i+1, len(V)):
            for v in V:
                if v != V[i] and v != V[j]:
                    if is_triple(G,(V[i],V[j],v),R1,R2):
                        if (V[i],V[j]) in triples.keys():
                            triples[V[i],V[j]].append(v)
                        else:
                            triples[V[i],V[j]] = [v]
    
    return triples

def triple_subset(R : dict, L : iter) -> dict:
    '''
    

    Parameters
    ----------
    R : dict
        triples.
    L : iter
        leaves/vertices to restrict R.

    Returns
    -------
    dict
        R restricted by L.

    '''
    return {(x,y):[z for z in R[x,y] if z in L] for x,y in R.keys() if x in L and y in L}

def triple_dict_to_list(R : dict) -> list:
    '''
    

    Parameters
    ----------
    R : dict
        triples (x,y):[*] for xy|*.

    Returns
    -------
    list
        triples (x,y,*).

    '''
    return [(x,y,z) for x,y in R.keys() for z in R[x,y]]

def triple_list_to_dict(R : list) -> dict:
    '''
    

    Parameters
    ----------
    R : list
        triples (x,y,*) for xy|*.

    Returns
    -------
    dict
        (x,y):[*].

    '''
    D = {(x,y):[] for x,y,_ in R}
    list(map(lambda x: D[x[0],x[1]].append(x[2]), R))
    return D

def triple_copy(R : dict) -> dict:
    """
    Makes non-shallow copy of dictionary

    Parameters
    ----------
    R : dict
        DESCRIPTION.

    Returns
    -------
    dict
        DESCRIPTION.

    """
    return {(x,y):[z for z in R[x,y]] for x,y in R}
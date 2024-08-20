# -*- coding: utf-8 -*-

import networkx as nx
from networkx import community as com
from graphs import *
from tralda import cograph as co, supertree as st
from triples import *
import random as rand
import math

__author__ = "Timothy Lindquist"

def direct_graph_cut(G_ : nx.Graph, half_cut = False, R1 = True, R2 = True, init=True) -> nx.Graph:
    '''
    Applies weights and cuts directly on G with edge weights based on R(G)
    until it is a cograph.

    Parameters
    ----------
    G_ : nx.Graph
    
    init : bool, optional
        Stops function from recomputing R(G). The default is True.

    Returns
    -------
    nx.Graph
        A cograph.

    '''
    if co.LinearCographDetector(G_).recognition():
        return G_
    
    G = G_.copy()
    comps = list(nx.connected_components(G))
    
    if init:
        R = get_triples(G,R1,R2)
        
        for x,y in R:
            if G.has_edge(x,y):
                G.edges[x,y]["weight"] = len(R[x,y])
            # Alternative weight function
            # else:
            #     if not R2:
            #         for z in R[x,y]:
            #             if "weight" not in G.edges[x,z]:
            #                 G.edges[x,z]["weight"] = 1
            #             else:
            #                 G.edges[x,z]["weight"] += 1
            #             if "weight" not in G.edges[y,z]:
            #                 G.edges[y,z]["weight"] = 1
            #             else:
            #                 G.edges[y,z]["weight"] += 1
                    
        for x,y in G.edges:
            if "weight" not in G.edges[x,y]:
                G.edges[x,y]["weight"] = 0

    if len(comps) > 1:
        Gnew = nx.Graph()
        for comp in comps:
            G_comp = G.copy()
            G_comp.remove_nodes_from([v for v in G.nodes if v not in comp])
            G_new = union(Gnew, direct_graph_cut(G_comp,half_cut,R1,R2,False))
        return Gnew
    
    
    if half_cut:
        V1,V2 = com.kernighan_lin_bisection(G)
    else:
        V1,V2 = nx.stoer_wagner(G)[1]
        
    current_edges = list(G.edges)
    G2 = G.copy()
    G.remove_nodes_from(V2)
    G2.remove_nodes_from(V1)
    G = direct_graph_cut(G,half_cut,R1,R2,False)
    G2 = direct_graph_cut(G2,half_cut,R1,R2,False)

    G_add = join(G,G2)
    G_del = union(G,G2)
    E_add = list(G_add.edges)
    E_del = list(G_del.edges)
    if n_sub_edits(current_edges, E_add) <\
        n_sub_edits(current_edges, E_del):
            return G_add
    return G_del
    
def minimal_graph_cut(G : nx.Graph,\
                      iterations : int = 5,\
                      half_cut : bool = False,\
                      R1 : bool = True, R2 : bool = True,\
                      init : bool = True):
    
    G2 = direct_graph_cut(G,half_cut,R1,R2,init)
    best_score = math.inf
    cut_edges = [(x,y) for x,y in G.edges if not G2.has_edge(x, y)]
    added_edges = [(x,y) for x,y in G2.edges if not (G.has_edge(x,y))]     
    edited_edges = cut_edges + added_edges
    for _ in range(iterations):
        G_tmp = G2.copy()
        rand.shuffle(edited_edges)
        for x,y in edited_edges:
            if G_tmp.has_edge(x, y):
                G_tmp.remove_edge(x,y)
                if not co.LinearCographDetector(G_tmp).recognition():
                    G_tmp.add_edge(x,y)
            else:
                G_tmp.add_edge(x,y)
                if not co.LinearCographDetector(G_tmp).recognition():
                    G_tmp.remove_edge(x,y)
        if n_edits(G, G_tmp) <= best_score:
            G_min = G_tmp
            
    return G_min

def min_edit(G):
    return co.to_cograph(co.edit_to_cograph(G))

def min_cut_split(R : dict, L : iter,\
                  half_cut : bool = False, init : bool = True) -> dict:
    '''
    Finds a consistent subset of R by using BUILD and a balanced min-cut.

    Parameters
    ----------
    R : dict
        Triples.
    L : list or iter
        Leaves/vertices.
    init : bool, optional
        Used to make sure the original triple set is not overwritten.
        The default is True.

    Returns
    -------
    dict
        Consistent subset of triples.
    
    References
    ----------
    Aho, Alfred V., et al. "Inferring a tree from lowest common ancestors with
    an application to the optimization of relational expressions."
    SIAM Journal on Computing 10.3 (1981): 405-421.
    '''
    
    if len(L) < 3:
        return R
    if init:
        # make copy
        R = {(x,y):R[x,y] for x,y in R}
    
    CG = comp_graph(R, L)
    comps = list(nx.connected_components(CG))
    
    if len(comps) > 1:
        for comp in comps:
            R = min_cut_split(R,comp,half_cut,init=False)
    else:
        # Cut if Aho graph is connected
        if half_cut:
            V1,V2 = com.kernighan_lin_bisection(CG)
        else:
            V1,V2 = nx.stoer_wagner(CG)[1]
        cut = [(x,y) for x,y in CG.edges if ((x in V1 and y in V2) or (x in V2 and y in V1))]
        for x,y in cut:
            try:
                R[x,y] = [z for z in R[x,y] if z not in CG.nodes]
            except:
                tmp = x
                x = y
                y = tmp
                R[x,y] = [z for z in R[x,y] if z not in CG.nodes]
            if len(R[x,y]) == 0:
                R.pop((x,y))
        if len(V1) > 2:
            R = min_cut_split(R,V1,half_cut,init=False)
        if len(V2) > 2:
            R = min_cut_split(R,V2,half_cut,init=False)
   
    return R

def min_cut_edit(G : nx.Graph, half_cut : bool = False,\
                 R1 : bool = True, R2 : bool = True) -> nx.Graph:
    R = get_triples(G,R1,R2)
    R_new = min_cut_split(R,G.nodes,half_cut)
    
    #H = triples_to_cograph(R_new, G.nodes) # Old method
    H = BUILD_cograph(R_new, G.nodes)
    H_comp = nx.complement(H)
    
    if n_edits(G, H) < n_edits(G, H_comp):
        return H
    return H_comp

def minimal_min_cut_edit(G : nx.Graph, iterations : int = 1,\
                         half_cut : bool = False, R1 : bool = True,\
                         R2 : bool = True) -> nx.Graph:
    H = min_cut_edit(G,half_cut,R1,R2)
    
    cut_edges = [(x,y) for x,y in G.edges if not H.has_edge(x,y)]
    best_score = len(G.edges)
            
    for _ in range(iterations):
        G_tmp = H.copy()
        rand.shuffle(cut_edges)
        for x,y in cut_edges:
            G_tmp.add_edge(x,y)
            if not co.LinearCographDetector(G_tmp).recognition():
                G_tmp.remove_edge(x,y)
        if n_deletions(G, G_tmp) < best_score:
            G_min = G_tmp
    return G_min
    
def n_deletions(G,H):
    n = 0
    for x,y in G.edges:
        if not H.has_edge(x,y):
            n += 1
    return n

def n_edits(G,H):
    n = 0
    # Count edge deletions
    for x,y in G.edges:
        if not H.has_edge(x,y):
            n += 1
    # Count edge additions
    for x,y in H.edges:
        if not G.has_edge(x,y):
            n += 1
    return n

def n_sub_edits(E, E_edited):
    added_edges = set(E_edited).difference(E)
    removed_edges = set(E).difference(E_edited)
    return len(added_edges) + len(removed_edges)

def random_editing(G):
    G = G.copy()
    n = len(G.nodes)
    edges = list(G.edges)
    if len(edges) < (n**2 - n)/2:
        rand.shuffle(edges)
        while not co.LinearCographDetector(G).recognition():
            x,y = edges.pop()
            G.remove_edge(x,y)
        return G
    edges = list(nx.complement(G).edges)
    while not co.LinearCographDetector(G).recognition():
        x,y = edges.pop()
        G.add_edge(x,y)
    return G
    
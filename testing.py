# -*- coding: utf-8 -*-
import networkx as nx
from networkx import community as com
from tralda import cograph as co, supertree as st
from triples import *
from graphs import *
from editing import *
import pandas as pd
import matplotlib.pyplot as plt 
import os
import math

__author__ = "Timothy Lindquist"

method_dict = {
    "EDT":"Minimal Cograph Editing",
    "DGC":"Direct Graph Cut",
    "DG1":"Direct Graph Cut without R2",
    "DHC":"Direct Graph Half-Cut",
    "DH1":"Direct Graph Half-Cut without R2",
    "MCS":"Min-Cut-Split",
    "MC1":"Min-Cut-Split without R2",
    "HCS":"Half-Cut-Split",
    "HC1":"Half-Cut-Split without R2",
    "RND": "Random Edge Completion"}

def editing_score(G,method):
    if method == "EDT":
        H = min_edit(G)
    if method == "DGC":
        H = minimal_graph_cut(G)
    if method == "DG1":
        H = minimal_graph_cut(G,R2=False)
    if method == "DHC":
        H = minimal_graph_cut(G,half_cut=True)
    if method == "DH1":
        H = minimal_graph_cut(G,half_cut=True,R2=False)
    if method == "MCS":
        H = minimal_min_cut_edit(G)
    if method == "MC1":
        H = minimal_min_cut_edit(G,R2=False)
    if method == "HCS":
        H = minimal_min_cut_edit(G,half_cut=True)
    if method == "HC1":
        H = minimal_min_cut_edit(G,half_cut=True,R2=False)
    if method == "RND":
        H = random_editing(G)
        return n_deletions(G, H)
    return n_edits(G,H)
def method_mean(methods,n,disturbances,times):
    if methods == "All":
        methods = method_dict.keys()
    all_scores = {m : [] for m in methods}
    for d in disturbances:
        scores = {m : 0 for m in methods}
        for _ in range(times):
            G = disturbed_random_cograph(n, d)
            for m in methods:
                scores[m] += editing_score(G, m)/times
        for m in methods:
            all_scores[m] += [scores[m]]
    for m in methods:
        plt.plot(disturbances,all_scores[m],label=method_dict[m])
    
    plt.xlabel("Disturbances")
    plt.ylabel("Edits")
    plt.title("Edge edits per method for "+ str(n) + " vertices")
    plt.legend(bbox_to_anchor = (1.62, 0.5), loc='center right')
    plt.show()
        
def method_min(methods,n,disturbances,times):
    if methods == "All":
        methods = method_dict.keys()
    all_scores = {m : [] for m in methods}
    for d in disturbances:
        scores = {m : math.inf for m in methods}
        for _ in range(times):
            G = disturbed_random_cograph(n, d)
            for m in methods:
                scores[m] = min(scores[m],editing_score(G, m))
        for m in methods:
            all_scores[m] += [scores[m]]
    for m in methods:
        plt.plot(disturbances,all_scores[m],label=method_dict[m])
    
    plt.xlabel("Disturbances")
    plt.ylabel("Edits")
    plt.title("Best case per method for "+ str(n) + " vertices")
    plt.legend()
    plt.show()
    
def method_max(methods,n,disturbances,times):
    if methods == "All":
        methods = method_dict.keys()
    all_scores = {m : [] for m in methods}
    for d in disturbances:
        scores = {m : 0 for m in methods}
        for _ in range(times):
            G = disturbed_random_cograph(n, d)
            for m in methods:
                scores[m] = max(scores[m],editing_score(G, m))
        for m in methods:
            all_scores[m] += [scores[m]]
    for m in methods:
        plt.plot(disturbances,all_scores[m],label=method_dict[m])
    
    plt.xlabel("Disturbances")
    plt.ylabel("Edits")
    plt.title("Worst case per method for "+ str(n) + " vertices")
    plt.legend()
    plt.show()

def test_performance(methods,n,disturbances,times):
    if methods == "All":
        methods = method_dict.keys()
    all_scores = {m : [] for m in methods}
    all_min_scores = {m : [] for m in methods}
    all_max_scores = {m : [] for m in methods}
    for d in disturbances:
        scores = {m : 0 for m in methods}
        highscores = {m : 0 for m in methods}
        lowscores = {m : math.inf for m in methods}
        for _ in range(times):
            G = disturbed_random_cograph(n, d)
            for m in methods:
                score = editing_score(G, m)
                scores[m] += score/times
                highscores[m] = max(highscores[m],score)
                lowscores[m] = min(lowscores[m],score)
        for m in methods:
            all_scores[m] += [scores[m]]
            all_min_scores[m] += [lowscores[m]]
            all_max_scores[m] += [highscores[m]]
    plt.figure(dpi=300)
    for m in methods:
        plt.plot(disturbances,all_scores[m],label=method_dict[m])
    plt.xlabel("Disturbances")
    plt.ylabel("Edits")
    plt.title("Mean edits for "+ str(n) + " vertices")
    plt.legend(bbox_to_anchor = (1.62, 0.5), loc='center right')
    plt.show()
    
    plt.figure(dpi=300)
    for m in methods:
        plt.plot(disturbances,all_min_scores[m],label=method_dict[m])
    
    plt.xlabel("Disturbances")
    plt.ylabel("Edits")
    plt.title("Fewest edits for "+ str(n) + " vertices")
    plt.legend(bbox_to_anchor = (1.62, 0.5), loc='center right')
    plt.show()
    
    plt.figure(dpi=300)
    for m in methods:
        plt.plot(disturbances,all_max_scores[m],label=method_dict[m])
    
    plt.xlabel("Disturbances")
    plt.ylabel("Edits")
    plt.title("Most edits for "+ str(n) + " vertices")
    plt.legend(bbox_to_anchor = (1.62, 0.5), loc='center right')
    plt.show()
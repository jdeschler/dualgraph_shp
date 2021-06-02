###################
# edges.py
# module for help visualizing edges of a GerryChain dual graph
# 
# - Jack Deschler
###################

from gerrychain import Graph
import pandas as pd
import geopandas as gpd
import networkx as nx
import matplotlib.pyplot as plt
from shapely.geometry import  LineString

##########
# plot_problems()
#  given a graph and a shapefile, plots the unconnected components in yellow
#   and the largest component in purple
#
# graph: the dual graph
# shp:   the associated shapefile
# key:   the unique identifier for each shape in the shapefile
#
# returns
#  a list of the shapes that are not in the largest component
#
# adapted from GerryChain docs: https://gerrychain.readthedocs.io/en/latest/
def plot_problems(graph, shp, key = "GEOID10"):
    components = list(nx.connected_components(graph))
    print([len(c) for c in components])
    biggest_component_size = max(len(c) for c in components)
    problem_components = [c for c in components if len(c) != biggest_component_size]
    problem_nodes = [node for component in problem_components for node in component]
    problem_geoids = [graph.nodes[node][key] for node in problem_nodes]

    is_a_problem = shp[key].isin(problem_geoids)
    shp.plot(column=is_a_problem, figsize=(10, 10))
    plt.axis('off')
    plt.show()
    return problem_geoids

##########
# plot_components()
#  given a graph and a shapefile, plots the different components in 
#   all differenc colors
#
# graph: the dual graph
# shp:   the associated shapefile
# key:   the unique identifier for each shape in the shapefile
#
# returns
#  nothing
def plot_components(graph, shp, key = "GEOID10"):
    components = list(nx.connected_components(graph))
    print([len(c) for c in components])
    keys_comps = [[graph.nodes[n]['VTD'] for n in c] for c in components]
    
    component_nums = []
    for k in list(shp[key]):
        for c in range(len(keys_comps)):
            if k in keys_comps[c]:
                component_nums += [c]
                break
    
    shp.plot(column=pd.Series(component_nums), figsize=(10, 10), cmap = 'tab10')
    plt.axis('off')
    plt.show()


########
# find_node_by_key()
#  finds a node in a graph by a column value
#
# keyval: the lookup target value
# graph:  the graph in which to search
# key:    column in which to search for the target value
#
# returns
#  success - the node where node[key] == keyval
#  failure - -1
#
# adapted from GerryChain docs: https://gerrychain.readthedocs.io/en/latest/
def find_node_by_key(keyval, graph, key = "GEOID10",):
    for node in graph:
        if graph.nodes[node][key] == keyval:
            return node
    return -1


#######
# edges_geoms()
#  retrieves the geometries of the end points of each edge in a graph
#  likely only ever to be called by the two functions below
# 
# graph: the graph to pull edges from
# shp:   the associated shapefile, with the geometries
# key:   the primary key unique identifier of the shapefile
#
# returns
#  list of (u,v) pairs, where u and v are the geometries of each respective edge's endpoints
def edges_geoms(graph, shp, key = "GEOID10"):
    key_dict = {}
    for _idx, row in shp.iterrows():
        key_dict[row[key]] = row['geometry']
    edges = list(graph.edges)
    nodes = [((graph.nodes[u]), (graph.nodes[v])) for u,v in edges]
    keys = [(n1[key], n2[key]) for n1, n2 in nodes]
    geoms = [(key_dict[k1], key_dict[k2]) for k1,k2 in keys]
    return geoms

#######
# edges_to_gdf
#   turns the edges of a graph into a GeoDataFrame with the centroids of the polygons as endpoints
# 
# graph: graph to pull edges from
# shp:   associated shapefile with geometries
# key:   primary key unique identifier of shapefile
#
# returns
#  a GeoDataFrame of edges as LineStrings, projected to the crs of `shp`
def edges_to_gdf(graph, shp, key = "GEOID10"):
    dual = gpd.GeoDataFrame(gpd.GeoSeries([LineString([poly1.centroid, poly2.centroid]) for poly1,poly2 in edges_geoms(graph, shp, key = key)]), columns = ['geometry'])
    return dual.set_crs(shp.crs)
    
#######
# edges_to_shapefile()
#  writes edges of a dual graph to a shapefile, with polygons centroids as endpoints
#  equivalent to running edges_to_gdf followed by gpd.to_file, without the return value in between
# 
# graph:   graph to pull edges from
# shp:     associated shapefile with geometries, resulting file will have this shapefiles projection
# key:     primary key unique identifier of shapefile
# outfile: file path to print shapefile
#
# returns
#  nothing
def edges_to_shapefile(graph, shp, key = "GEOID10", outfile = "outfile.shp"):
    dual = gpd.GeoDataFrame(gpd.GeoSeries([LineString([poly1.centroid, poly2.centroid]) for poly1,poly2 in edges_geoms(graph, shp, key = key)]), columns = ['geometry'])
    dual = dual.set_crs(shp.crs)
    dual.to_file(outfile)

##########
# edges_geoms_endpoints, edges_to_gdf_endpoints, edges_to_shapefile_endpoints
#
#  These functions do the same things as the three above (without _endpoints),
#  with the exception that the resulting GeoDataFrame and shapefile have a value
#  from each edge's endpoints. The stored value is controlled by passing the 
#  `endpoints` argument to each function, and should typically be a unique identifier
#  for a node. The endpoints are stored in columns `endpoint_u` and `endpoint_v`.
#  Ordering between u and v is set by the networkx graph object.
def edges_geoms_endpoints(graph, shp, endpoints = "GEOID10", key = "GEOID10"):
    key_dict = {}
    endpoint_dict = {}
    for _idx, row in shp.iterrows():
        key_dict[row[key]] = row['geometry']
        endpoint_dict[row[key]] = row[endpoints]
    edges = list(graph.edges)
    nodes = [((graph.nodes[u]), (graph.nodes[v])) for u,v in edges]
    keys = [(n1[key], n2[key]) for n1, n2 in nodes]
    geoms = [(key_dict[k1], key_dict[k2]) for k1,k2 in keys]
    endpoints = [(endpoint_dict[k1], endpoint_dict[k2]) for k1,k2 in keys]
    return (geoms, endpoints)

def edges_to_gdf_endpoints(graph, shp, endpoints = "GEOID10", key = "GEOID10"):
    geos, endpoints = edges_geoms_endpoints(graph, shp, endpoints = endpoints, key = key)
    ends_u, ends_v = zip(*endpoints)
    dual = gpd.GeoDataFrame(zip(ends_u, ends_v, gpd.GeoSeries([LineString([poly1.centroid, poly2.centroid]) for poly1,poly2 in geos])), columns = ['endpoint_u','endpoint_v','geometry'])
    return dual.set_crs(shp.crs)
    
def edges_to_shapefile_endpoints(graph, shp, endpoints = "GEOID10", key = "GEOID10", outfile = "outfile.shp"):
    geos, endpoints = edges_geoms_endpoints(graph, shp, endpoints = endpoints, key = key)
    ends_u, ends_v = zip(*endpoints)
    dual = gpd.GeoDataFrame(zip(ends_u, ends_v, gpd.GeoSeries([LineString([poly1.centroid, poly2.centroid]) for poly1,poly2 in geos])), columns = ['endpoint_u','endpoint_v','geometry'])
    dual = dual.set_crs(shp.crs)
    dual.to_file(outfile)

####################
# shared_boundaries_gdf
#   stores the boundaries crossed by the edges of a dual graph
# 
# graph: graph to pull edges from
# g_shp: shapefile of the graph with endpoint columns - should have been created
#         by `edges_to_gdf_endpoints`
# shp:   associated shapefile with geometries
# key:   primary key unique identifier of shapefile, must match key in endpoint columns
#
# returns
#  a GeoDataFrame of crossed boundaries as MultiLineStrings, projected to the crs of `shp`
def shared_boundaries_gdf(graph, g_shp, shp, key = "GEOID10"):
    key_dict = {}
    for _idx, row in shp.iterrows():
        key_dict[row[key]] = row['geometry']
    es = zip(g_shp['endpoint_u'], g_shp['endpoint_v'])
    nodes = [(find_node_by_key(u, graph, key = key), find_node_by_key(v, graph, key = key)) for u,v in es]
    keys = [(graph.nodes[n1][key], graph.nodes[n2][key]) for n1, n2 in nodes]
    geoms = [(key_dict[k1], key_dict[k2]) for k1,k2 in keys]
    overlaps = gpd.GeoDataFrame(gpd.GeoSeries([p1.intersection(p2) for p1,p2 in geoms]), columns = ['geometry'])
    overlaps = overlaps.set_crs(shp.crs)
    overlaps['endpoint_u'] = g_shp['endpoint_u']
    overlaps['endpoint_v'] = g_shp['endpoint_v']
    return overlaps

########
# [remove/add]_edge_by_feature()
#  either removes or adds an edge between nodes that have certain values in a column
#
# graph: the graph to edit
# u_key: key value of one endpoint
# v_key: key value of second endpoint
# key:   the column/attribute to compare to the given values
#
# returns
#  graph with the edge added or removed
def remove_edge_by_feature(graph, u_key, v_key, key):
    u = find_node_by_key(u_key, graph, key = key)
    v = find_node_by_key(v_key, graph, key = key)
    graph.remove_edge(u,v)
    return graph

def add_edge_by_feature(graph, u_key, v_key, key):
    u = find_node_by_key(u_key, graph, key = key)
    v = find_node_by_key(v_key, graph, key = key)
    graph.add_edge(u,v)
    return graph

########
# mark_edges
#  sets a column value in a from-graph GeoDataFrame for a list of edges
#
# g_shp: a GeoDataFrame made from a graph, MUST have endpoint columns `endpoint_u` and `endpoint_v`
#         function `edges_to_gdf_endpoints` produces a proper GeoDataFrame for this function
# marks: list of tuples, each tuple being a (u,v) pair where u and v will be matched against
#          values in the endpoint columns of g_shp, order of (u,v) and (v,u) will both get marked
#          if feeding in GeoDataFrame from `edges_to_gdf_endpoints` the values in `marks` tuples
#          should be from the column passed to the `edges_to_gdf_endpoints` in the `endpoints` argument
# col:   column to mark each edge in, if it does not already exist, will be created and initialized to 0
# val:   value to mark for each row in column, by varying 'col' and 'val', one can call this multiple times
#          on the same GeoDataFrame, and mark multiple lists of edges with different values in the same
#          column, or the same value in different column
#
# returns
#  a GeoDataFrame with edges from `marks` marked with `val` in the column `col`
def mark_edges(g_shp, marks, col = "marked", val = 1):
    if col not in list(g_shp):
        g_shp[col] = 0
    for u,v in marks:
        # try u,v
        g_shp.loc[(g_shp['endpoint_u'] == u) & (g_shp['endpoint_v'] == v), col] = val
        # try v,u
        g_shp.loc[(g_shp['endpoint_v'] == u) & (g_shp['endpoint_u'] == u), col] = val
    return g_shp

########
# mark_edges_dict
#  sets a column value in a from-graph GeoDataFrame for a list of edges
#
# g_shp: a GeoDataFrame made from a graph, MUST have endpoint columns `endpoint_u` and `endpoint_v`
#         function `edges_to_gdf_endpoints` produces a proper GeoDataFrame for this function
# marks: dict of tuples, each tuple being a (u,v) pair where u and v will be matched against
#          values in the endpoint columns of g_shp, order of (u,v) and (v,u) will both get marked
#          if feeding in GeoDataFrame from `edges_to_gdf_endpoints` the values in `marks` tuples
#          should be from the column passed to the `edges_to_gdf_endpoints` in the `endpoints` argument
# col:   column to mark each edge in, if it does not already exist, will be created and initialized to 0
#
# returns
#  a GeoDataFrame with edges from `marks` marked with the corresponding value from `marks`
#  in the column `col`
def mark_edges_dict(g_shp, marks, col = "marked"):
    if col not in list(g_shp):
        g_shp[col] = 0
    for k,val in marks.items():
        u = k[0]
        v = k[1]
        # try u,v
        g_shp.loc[(g_shp['endpoint_u'] == u) & (g_shp['endpoint_v'] == v), col] = val
        # try v,u
        g_shp.loc[(g_shp['endpoint_v'] == u) & (g_shp['endpoint_u'] == u), col] = val
    return g_shp
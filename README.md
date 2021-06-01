# `edges` module
Python functions for turning `GerryChain` dual graphs into shapefiles and `geopandas` GeoDataframes. Found in `edges.py`.

## **Visualization Functions**
### `plot_problems`
Plots the unconnected components of a graph in yellow and the largest connected component in purple. _Adapted from GerryChain [documentation](https://gerrychain.readthedocs.io/en/latest/)_.

#### Inputs
* **graph**: the dual graph
* **shp**:   the associated shapefile
* **key**:   the unique identifier for each shape in the shapefile

#### Outputs
* returns a list of the `key` value of shapes that are not in the largest component
* shows a plot of the shapefile, colored by the graph's connected components, with the biggest component in purple, and all others in yellow


### `plot_components`
Given a graph and a shapefile, plots the different components in all different colors
#### Inputs
* **graph**: the dual graph
* **shp**:   the associated shapefile
* **key**:   the unique identifier for each shape in the shapefile

#### Outputs
* returns nothing
* shows a plot of the shapefile, with each connected component in a different color

## **Graphs to Shapefiles and GeoDataFrames**

### `edges_to_gdf`
Turns the edges of a graph into a GeoDataFrame with the centroids of the polygons as endpoints of each edge.

#### Inputs
* **graph**: graph to pull edges from
* **shp**: associated shapefile with geometries
* **key**: primary key unique identifier of shapefile

#### Outputs
* returns a GeoDataFrame of edges as LineStrings, projected to the crs of `shp`
    

### `edges_to_shapefile`
Writes edges of a dual graph to a shapefile, with polygons centroids as endpoints. Equivalent to running `edges_to_gdf` followed by `gpd.to_file`.

#### Inputs
* **graph**:   graph to pull edges from
* **shp**:     associated shapefile with geometries, resulting file will have this shapefiles projection
* **key**:     primary key unique identifier of shapefile
* **outfile**: file path to print shapefile, should end in ".shp"

#### Outputs
* returns nothing
* writes the resultant shapefile to `outfile`

### `edges_to_gdf_endpoints`, `edges_to_shapefile_endpoints`
These functions do the same things as the three above (without `_endpoints`), with the exception that the resulting GeoDataFrame and shapefile have a value from each edge's endpoints. The stored value is controlled by passing the `endpoints` argument to each function, and should typically be a unique identifier for a node. The endpoints are stored in columns `endpoint_u` and `endpoint_v`. Ordering between u and v is set by the networkx graph object.

### `mark_edges`
Sets a column value in a from-graph GeoDataFrame for a list of edges

#### Inputs
* **g_shp**: a GeoDataFrame made from a graph, MUST have endpoint columns `endpoint_u` and `endpoint_v` function `edges_to_gdf_endpoints` produces a proper GeoDataFrame for this function
* **marks**: list of tuples, each tuple being a (u,v) pair where u and v will be matched against values in the endpoint columns of g_shp, order of (u,v) and (v,u) will both get marked. If feeding in GeoDataFrame from `edges_to_gdf_endpoints` the values in `marks` tuples should be from the column passed to the `edges_to_gdf_endpoints` in the `endpoints` argument
* **col**: column to mark each edge in, if it does not already exist, will be created and initialized to 0
* **val**: value to mark for each row in column, by varying 'col' and 'val', one can call this multiple times on the same GeoDataFrame, and mark multiple lists of edges with different values in the same column, or the same value in different column

#### Outputs
* returns a GeoDataFrame with edges from `marks` marked with `val` in the column `col`


### `mark_edges_dict`
Sets a column value in a from-graph GeoDataFrame with a dictionary of edge tuples. Unlike `mark_edges`, allows different edges to be set to different edges in one pass

#### Inputs
* **g_shp**: a GeoDataFrame made from a graph, MUST have endpoint columns `endpoint_u` and `endpoint_v` function `edges_to_gdf_endpoints` produces a proper GeoDataFrame for this function
* **marks**: dict of tuples, each tuple being a (u,v) pair where u and v will be matched against values in the endpoint columns of g_shp, order of (u,v) and (v,u) will both get marked. If feeding in GeoDataFrame from `edges_to_gdf_endpoints` the values in `marks` tuples should be from the column passed to the `edges_to_gdf_endpoints` in the `endpoints` argument. **MUST** be of the form `(u,v): value` where `u` and `v` match the endpoint columns in `g_shp`
* **col**: column to mark each edge in, if it does not already exist, will be created and initialized to 0

#### Outputs
* returns a GeoDataFrame with edges from `marks` marked with the corresponding value in the column `col`

## **Helper functions**
### `find_node_by_key`
Finds a node in a graph by a column value. _Adapted from GerryChain [documentation](https://gerrychain.readthedocs.io/en/latest/)_.

#### Inputs
* **keyval**: the lookup target value
* **graph**:  the graph in which to search
* **key**:    column in which to search for the target value

#### Outputs
* returns
    * success - the node where `node[key] == keyval`
    * failure - `-1`


### `edges_geoms`
R etrieves the geometries of the end points of each edge in a graph. Likely only ever to be called as a helper by `edges_to_shapefile` and `edges_to_gdf`

#### Inputs
* **graph**: the graph to pull edges from
* **shp**: the associated shapefile, with the geometries
* **key**: the primary key unique identifier of the shapefile

#### Outputs
* returns list of `(u,v)` pairs, where `u` and `v` are the geometries of each respective edge's endpoints

### `edges_geoms_endpoints`
This function does the same work as `edges_geoms` for the `_endpoints` series of functions (see below). It takes an additional argumen `endpoints`, which is the shapefile column value of each node to store as the endpoints for each edge. Ordering between u and v is set by the `networkx` graph object.


### `[remove/add]_edge_by_feature`
Either removes or adds an edge between nodes that have certain values in a column

#### Inputs
* **graph**: the graph to edit
* **u_key**: key value of one endpoint
* **v_key**: key value of second endpoint
* **key**: the column/attribute to compare to the given values

#### Outputs
* returns the graph with the edge added or removed

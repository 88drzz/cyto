import py4cytoscape as p4c
import json
import pandas as pd

# Retrieve the nodes and edges of the current network.
nodes = p4c.get_table_columns('node')
edges = p4c.get_table_columns('edge')

# Print the column names of the node table and edge table (for debugging purposes).
print("Node columns:", nodes.columns)
print("Edge columns:", edges.columns)

# Retrieve the color properties of all nodes and format them according to the format used in a successful case.
node_colors = {}
light_node_colors = {}
def lighten_color(hex_color, factor=0.5):
    """ Lightens the given color by the given factor (0.0 - 1.0). """
    hex_color = hex_color.lstrip('#')
    rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    light_rgb = tuple(int(c + (255 - c) * factor) for c in rgb)
    return '#{:02X}{:02X}{:02X}'.format(*light_rgb)
for node_suid in nodes['SUID']:
    try:
        # Retrieve the visual property (color) of the nodes.
        visual_props = p4c.get_node_property(node_suid, 'NODE_FILL_COLOR')
        color_hex = visual_props[node_suid] if isinstance(visual_props, dict) else visual_props
        color_hex = color_hex.upper() 
        node_colors[node_suid] = color_hex
        light_node_colors[node_suid] = lighten_color(color_hex)
        print(f"Node {node_suid} color: {color_hex}, light color: {light_node_colors[node_suid]}")  
    except Exception as e:
        print(f"Error retrieving color for node {node_suid}: {e}")
        node_colors[node_suid] = None
        light_node_colors[node_suid] = None

# Print the extracted node colors (for debugging purposes).
print("Node colors:", node_colors)
print("Light node colors:", light_node_colors)

# Assume that the 'shared name' column in the edge table is formatted as 'source (interaction) target'
# Create a function to parse the source node.
def parse_source_node(edge_name):
    try:
        source_node = edge_name.split(" (")[0]
        return source_node
    except Exception as e:
        print(f"Error parsing source node from edge name {edge_name}: {e}")
        return None

# Create a new dataframe to store the color information of edges.
edge_color_mapping = []

# Set the color of each edge to be the same as the color of its source node.
for index, row in edges.iterrows():
    edge_name = row['shared name']
    source_node_name = parse_source_node(edge_name)
    if source_node_name:
        print(f"Edge: {edge_name}, Source Node: {source_node_name}")  
        # Find the SUID of the source node.
        try:
            source_node_suid = nodes[nodes['name'] == source_node_name]['SUID'].values[0]
            print(f"Source node SUID for {source_node_name}: {source_node_suid}")
            if source_node_suid in node_colors:
                edge_color = node_colors[source_node_suid]
                edge_color_mapping.append({'shared name': row['shared name'], 'source_node_color': edge_color})
                print(f"Edge {row['shared name']} color: {edge_color}")  
            else:
                print(f"No color found for source node SUID: {source_node_suid}")
        except IndexError:
            print(f"Source node {source_node_name} not found in node table")
    else:
        print(f"Could not parse source node for edge: {edge_name}")

# Print the parsed edge color mapping (for debugging purposes).
print("Edge color mapping:", edge_color_mapping)

# Create a new dataframe
edge_color_df = pd.DataFrame(edge_color_mapping)

# Print the new dataframe to confirm that the data is correct.
print("Edge color DataFrame:\n", edge_color_df)

# Ensure that there is a 'source_node_color' column in the edge table.
if 'source_node_color' not in edges.columns:
    edges['source_node_color'] = None

# Ensure that there is a 'light_node_color' column in the edge table.
if 'light_node_color' not in edges.columns:
    edges['light_node_color'] = None

# Update the 'source_node_color' and 'light_node_color' columns in the edge table.
for index, row in edge_color_df.iterrows():
    edges.loc[edges['shared name'] == row['shared name'], 'source_node_color'] = row['source_node_color']
    edges.loc[edges['shared name'] == row['shared name'], 'light_node_color'] = lighten_color(row['source_node_color'])

# Print the updated edge table (for debugging purposes).
print("Updated edge table:\n", edges[['shared name', 'source_node_color', 'light_node_color']])

# Load the updated edge table back into Cytoscape.
p4c.load_table_data(edges, table='edge', table_key_column='shared name', data_key_column='shared name')
print("Edge colors updated in edge table.")


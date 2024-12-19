
import py4cytoscape as p4c
import pandas as pd

# Connect to Cytoscape
p4c.cytoscape_ping()

# Get the SUID of the current network
network_suid = p4c.get_network_suid()

# Obtain the SUIDs and related information for all edges
edges_table = p4c.get_table_columns('edge', columns=['SUID', 'shared name', 'weight'])

# Convert to a DataFrame for processing
edges_df = pd.DataFrame(edges_table)

# Calculate the transparency of edges
def calculate_transparency(weight, min_weight, max_weight, min_transparency=30, max_transparency=255):
    if max_weight == min_weight:
        return int(max_transparency)
    transparency = min_transparency + ((weight - min_weight) / (max_weight - min_weight) * (max_transparency - min_transparency))
    return int(transparency)

# Calculate transparency for each edge
transparency_values = []
min_weight = edges_df['weight'].min()
max_weight = edges_df['weight'].max()

for index, row in edges_df.iterrows():
    weight = row['weight']
    transparency = calculate_transparency(weight, min_weight, max_weight)
    transparency_values.append(transparency)

# Write the transparency values into the DataFrame.
edges_df['trans'] = transparency_values

# Print the transparency values for debugging purposes.
print("Transparency values:", transparency_values)

# Write the new transparency column back to Cytoscape.
p4c.load_table_data(data=edges_df[['SUID', 'trans']], data_key_column='SUID', table='edge', table_key_column='SUID', network=network_suid)

# Apply transparency mapping in the Style.
p4c.map_visual_property(visual_prop='EDGE_TRANSPARENCY', mapping_type='c', table_column='trans', 
                        table_column_values=[min(transparency_values), max(transparency_values)], 
                        visual_prop_values=[50, 200], network=network_suid)
print("New 'trans' column created and transparency mapping applied successfully.")

import pandas as pd
import numpy as np
import h5py

# # Load the HDF5 file
# file_path = "TRAAAAW128F429D538.h5"
# with h5py.File(file_path, "r") as hdf:
#     # List all groups
#     print("Groups in the file:")
#     for group in hdf.keys():
#         print(group)

#     # Access a specific group
#     metadata = hdf["metadata"]

#     # List datasets in the group
#     print("Datasets in 'metadata':")
#     for dataset in metadata.keys():
#         print(dataset)

# # Function to extract data
# def extract_data(file_path):
#     with h5py.File(file_path, "r") as hdf:
#         title = hdf["metadata"]["songs"]["title"][:]
#         artist = hdf["metadata"]["songs"]["artist_name"][:]
#         tempo = hdf["analysis"]["songs"]["tempo"][:]
#         duration = hdf["analysis"]["songs"]["duration"][:]
        
#         # Decode bytes to strings for textual data
#         title = [t.decode('utf-8') for t in title]
#         artist = [a.decode('utf-8') for a in artist]
        
#         # Create a DataFrame
#         df = pd.DataFrame({
#             "title": title,
#             "artist": artist,
#             "tempo": tempo,
#             "duration": duration,
#         })
#     return df

# # Load the data
# df = extract_data(file_path)

# # Preview the data
# print(df.head())

def print_hdf5_structure(name, obj):
    """
    Recursive function to print the structure of the HDF5 file.
    :param name: Path name of the current object.
    :param obj: HDF5 object (Group or Dataset).
    """
    if isinstance(obj, h5py.Group):
        print(f"Group: {name}")
    elif isinstance(obj, h5py.Dataset):
        print(f"  Dataset: {name}, Shape: {obj.shape}, Type: {obj.dtype}")

def inspect_hdf5_file(file_path):
    with h5py.File(file_path, "r") as hdf:
        for group_name, obj in hdf.items():
            print(f"\nGroup: {group_name}")
            for dataset_name, dataset in obj.items():
                print(f"  Dataset: {group_name}/{dataset_name}")
                print(f"    Shape: {dataset.shape}, Type: {dataset.dtype}")
                # Print a small preview of the data
                print(f"    Data (first 5 values): {dataset[:5]}")
                
# Path to your HDF5 file
file_path = "TRAAAAW128F429D538.h5"

# with h5py.File(file_path, "r") as hdf:
#     # Use visititems() to recursively iterate over all items in the file
#     hdf.visititems(print_hdf5_structure)
    
inspect_hdf5_file(file_path)
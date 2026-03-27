import streamlit as st
import streamlit.components.v1 as components
import os

# Define the component directory relative to this file
COMPONENT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "storage_component")

# The index.html is already created via git/write_to_file
# So we only need to declare the component

_storage_component = components.declare_component(
    "storage_component",
    path=COMPONENT_DIR
)

def get_local_storage(storage_key, streamlit_key=None):
    """Read a value from browser's localStorage."""
    return _storage_component(storage_key=storage_key, action="get", default=None, key=streamlit_key)

def set_local_storage(storage_key, value, streamlit_key=None):
    """Write a value to browser's localStorage."""
    return _storage_component(storage_key=storage_key, action="set", value=value, default=None, key=streamlit_key)

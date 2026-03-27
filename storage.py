import streamlit as st
import streamlit.components.v1 as components
import os

# Create a small HTML file for the component
COMPONENT_DIR = os.path.join(os.path.dirname(__file__), "storage_component")
if not os.path.exists(COMPONENT_DIR):
    os.makedirs(COMPONENT_DIR)

INDEX_PATH = os.path.join(COMPONENT_DIR, "index.html")
with open(INDEX_PATH, "w") as f:
    f.write("""
    <!DOCTYPE html>
    <html>
    <body>
        <script>
            function sendMessageToStreamlit(value) {
                window.parent.postMessage({
                    type: 'streamlit:setComponentValue',
                    value: value
                }, '*');
            }

            window.addEventListener("message", (event) => {
                if (event.data.type === "streamlit:render") {
                    const {key, action, value} = event.data.args;
                    if (action === "get") {
                        const stored = localStorage.getItem(key);
                        sendMessageToStreamlit(stored);
                    } else if (action === "set") {
                        localStorage.setItem(key, value);
                        sendMessageToStreamlit(value);
                    }
                }
            });
        </script>
    </body>
    </html>
    """)

_storage_component = components.declare_component(
    "storage_component",
    path=COMPONENT_DIR
)

def get_local_storage(key):
    return _storage_component(key=key, action="get", default=None)

def set_local_storage(key, value):
    return _storage_component(key=key, action="set", value=value, default=None)

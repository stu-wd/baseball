Two ways to get this started easily:
- write code in a '.py' file, then execute (similar to node.js) by running 'python3 {fileName}.py'
- run 'source .venv/bin/activate' to launch the virtual environment
  - run 'pip install notebook'
  - run 'jupyter notebook' to launch a browser version of the notebook
- to exit the virtual environment, run 'deactivate'

Tips:
- 'shift + enter' runs a block of highlighted code (runs all code if no highlight)

## Streamlit Dashboard

To launch the fantasy baseball dashboard:

1. Activate the virtual environment:
   ```
   source .venv/bin/activate
   ```
2. Install dependencies (first time only):
   ```
   pip install -r requirements.txt
   ```
3. Run the app:
   ```
   streamlit run dashboard.py
   ```

The app will open automatically in your browser at `http://localhost:8501`.
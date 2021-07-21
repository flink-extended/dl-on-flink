# Build Documents

### Requirement
1. Python3.7
2. Sphinx (You can install it via `pip install -U sphinx sphinx_rtd_theme`)
3. Flink AI Flow

### Build
```
cd flink-ai-flow/docs/
bash docgen.sh
make clean html
```

After building, you can view the local document in your browser by typing `open ./_build/html/index.html` in your terminal.

Or `python -m http.server ` to start a local server which enables users to view the documents on `http://0.0.0.0:8000/_build/html`.

# Showdown EV Simulator/Optimizer (Colab-ready)

## Use RAW GitHub links directly

If your CSVs live on GitHub, point pandas straight at the RAW URLs:

```python
# In Colab
import sys, zipfile, os

# 1) Upload the zip you downloaded to /content or replace the path below
zip_path = "/content/showdown_ev_pkg.zip"  # or mount Drive and point here
with zipfile.ZipFile(zip_path, 'r') as z:
    z.extractall("/content/")

sys.path.append("/content/showdown_ev")

from showdown.run_example import run

projections_url  = "https://raw.githubusercontent.com/<user>/<repo>/<branch>/projections.csv"
leverage_url     = "https://raw.githubusercontent.com/<user>/<repo>/<branch>/leverage.csv"
percentiles_url  = "https://raw.githubusercontent.com/<user>/<repo>/<branch>/percentiles.csv"

chosen, top = run(projections_url, leverage_url, percentiles_url)
chosen, top
```

> Tip: If you only have the *blob* link (e.g., `https://github.com/<user>/<repo>/blob/<branch>/file.csv`),
> convert it to RAW by switching to `https://raw.githubusercontent.com/<user>/<repo>/<branch>/file.csv`.

### What this does
- `load_projections`, `load_leverage`, and `load_percentiles` call `pd.read_csv(...)` on your URL.
- Everything else stays the same (candidate generation, field simulation, EV calc, portfolio selection).

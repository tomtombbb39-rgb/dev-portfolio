# Static Property Graph Analysis (Sample)

This sample project reads measurement CSV files and performs static-property analysis with graph plotting.

## Overview

The code automatically selects a processing class from the filename data type.
Supported data types are:

- `IdVd`
- `IdVg`
- `IfVf`
- `BV`

Main operations:

- `obj.data()` : calculate and print extracted values
- `obj.graph(xlim, ylim)` : plot the graph

## Repository Structure

- `StaticPropertyGraphAnalysis_Plot.py`
  - Runner script with `#%%` cells
  - Includes examples for single-file run, multi-device aggregation, and overlay plotting
- `STClass.py`
  - Core classes for reading, analysis, and plotting
  - `run_class()` auto-selects class by data type

## Requirements

Required libraries:

- `pandas`
- `numpy`
- `matplotlib`

```bash
pip install pandas numpy matplotlib
```

## Quick Start

1. Set CSV path to `file` or `file_dir` in `StaticPropertyGraphAnalysis_Plot.py`
2. Create object with `run_class(file)`
3. Run `obj.data()` and/or `obj.graph(...)`

Minimal example:

```python
import matplotlib.pyplot as plt
from STClass import run_class, Common

file = "file_path.csv"
xlim = None
ylim = None

obj = run_class(file)
Common.set_rcParams()
obj.data()
obj.graph(xlim, ylim)
plt.show()
```

## Optional Parameters

You can pass the following to `run_class()`:

- `label` : legend label
- `line_style` : line style (e.g. `"-"`, `"--"`, `":"`, `"-."`)
- `color` : line color (e.g. `"red"`, `"blue"`)
- `Ith` / `Jth` : threshold conditions for extraction
- `abs_mode` : use absolute value mode for `IfVf`

Default `Ith` values:

- `IdVg`: `20 mA`
- `IfVf`: `-20 mA`
- `BV`: `100 uA`

Use `abs_mode=True` when handling `IfVf` in absolute-value mode.

## File Naming Rule (Important)

Processing behavior depends on filename, so this naming convention is required:

```text
(directory)/(device_name)_(data_type)_(optional_info)_(device_number).csv
```

- Device name: must match a name defined in `DeviceData.py`
- Data type: `IdVd` / `IdVg` / `IfVf` / `BV` (case-sensitive)
- Device number: last token in filename (e.g. `1`, `2`, `3`)
- Optional info: free field such as temperature condition (e.g. `175`)

Examples:

```text
Wolfspeed_IfVf_Vgs-4V_1.csv
Onsemi_IdVg_175_1.csv
```

## CSV Format Assumption

`STClass.py` assumes a specific instrument CSV format.

- `pd.read_csv(..., skiprows=47, header=None)`
- Referenced columns:
  - `IdVd`: current=`9`, voltage=`12`
  - `IdVg`: current=`3`, voltage=`12`
  - `IfVf`: current=`9`, voltage=`12`
  - `BV`: current=`6`, voltage=`9`

If your CSV format differs, adjust `ReadFile.read_file()` in `STClass.py`.

## Notes for Public Repository

`STClass.py` imports device area values from `DeviceData`, but `DeviceData` contains private information and is intentionally excluded from this public repository.

To run the code, prepare `DeviceData.py` locally (required).


At minimum, `DeviceData.py` should contain:

- per-device `area`
- lists such as `devices` / `nums` (and `temps` if needed)

## Recommended Environment

- VSCode + Python extension
- `#%%` cell execution in Interactive Window


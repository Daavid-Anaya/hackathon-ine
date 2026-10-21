"""Comprueba Python, Pandas y Scikit-learn con datos sintéticos, sin archivos CCPC."""

import argparse
from importlib.metadata import version
import json
import platform
import sys


def main():
    if sys.version_info[:2] != (3, 12):
        raise RuntimeError("Utiliza el entorno documentado de Python 3.12")

    import numpy as np
    import pandas as pd
    from sklearn.preprocessing import StandardScaler

    frame = pd.DataFrame({"counts": [10, 20, 30], "totals": [20, 40, 60]})
    rates = frame["counts"] / frame["totals"]
    np.testing.assert_allclose(rates.to_numpy(), [0.5, 0.5, 0.5])
    scaled = StandardScaler().fit_transform(frame[["counts"]])
    np.testing.assert_allclose(scaled[:, 0], [-np.sqrt(1.5), 0, np.sqrt(1.5)])
    print(json.dumps({
        "python": platform.python_version(),
        "pandas": version("pandas"),
        "scikit-learn": version("scikit-learn"),
        "numpy": version("numpy"),
        "smoke_test": "ok",
    }, indent=2))


if __name__ == "__main__":
    argparse.ArgumentParser(description=__doc__).parse_args()
    main()

#!/bin/bash
# Install Python packages into the container overlay.
#
# This script is run by the system on the login node (which has internet)
# inside the container with a persistent overlay. Changes persist across
# job submissions without rebuilding the container.
#
# Put ALL pip installs here, NOT in container.def.
# Only use container.def for the base Docker image and apt-get packages.
#
# IMPORTANT: Install into the SYSTEM Python, not a virtual environment.
# The overlay may be recreated on container rebuilds — a venv inside
# it will be lost and all subsequent jobs will fail.
# Use: uv pip install --system <packages>
# Do NOT create a venv (python -m venv, virtualenv, etc.).

set -euo pipefail

# Pin NumPy to a Python 3.11 wheel first. Older Biotite releases pull NumPy
# 1.21, which has no cp311 wheel and times out compiling in the overlay.
uv pip install --system "numpy==1.26.4"

uv pip install --system \
  "pandas>=2.1,<3" \
  "scipy>=1.11,<2" \
  "scikit-learn>=1.4,<2" \
  "matplotlib>=3.8,<4" \
  "imageio>=2.34,<3" \
  "tqdm>=4.66,<5" \
  "sortedcontainers>=2.4,<3" \
  "biopython>=1.83,<2" \
  "biotite>=0.41,<1" \
  "torch>=2.2,<3" \
  "seaborn>=0.13,<1" \
  "mpl-scatter-density>=0.8,<1" \
  "astropy>=6,<8" \
  "requests>=2.31,<3" \
  "brotli>=1.1,<2" \
  "cloudpathlib>=0.18,<1" \
  "huggingface-hub>=0.23,<1"

uv pip install --system esm==3.2.0 --no-deps

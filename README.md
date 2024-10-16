# DFS NFL outcomes predictions and daily fantasy contest lineup generator

## Sub-packages
- [apps:](apps/README.md) Executable python scripts
- [dfsdata:](dfsdata/README.md) Database schemas, creation, connections, updates, and queries
- [dfsmc:](dfsmc/README.md) Matchup simulators and game/player projections
- [dfsopt:](dfsopt/README.md) Contest lineup optimizer
- [dfsutil:](dfsutil/README.md) Utilities and helpers
- [doc:](doc/README.md) Integrated documentation


# 1. Create a new conda environment with Python 3.11
conda create --name dlearning python=3.11

# 2. Activate the environment
conda activate dlearning

# 3. Install CUDA Toolkit 12.1.1 (if not already installed)
# Download and install from: https://developer.nvidia.com/cuda-downloads

# 4. Install PyTorch 2.3.1 with CUDA 12.1 support using pip
pip install torch==2.3.1 torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# 5. Verify PyTorch installation and CUDA availability
python -c "import torch; print(torch.__version__); print(torch.cuda.is_available())"
2.3.1+cu121
True
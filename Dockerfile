FROM nvidia/cuda:12.2.0-base-ubuntu22.04

# Install system dependencies and clean up
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        python3 \
        python3-pip \
        python3-dev \
        build-essential \
        wget \
        curl && \
    rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN python3 -m pip install --upgrade pip

WORKDIR /workspace

# Expose application port
EXPOSE 52000

# To run the container with unlimited memory, port mapping, workspace mount, and a specific name:
# docker run --gpus all -it --name Omniparser-v2 -v /mnt/c/git/OmniParser:/workspace omniparserv2:latest 

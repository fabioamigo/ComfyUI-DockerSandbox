# Docker Sandbox Runner for ComfyUI

This **Custom Node** provides a secure, isolated execution environment for Python scripts within ComfyUI, utilizing persistent Docker containers. Code execution is ultra-fast (milliseconds) and completely isolated from the host operating system.

-----

## Key Features

  * **Maximum Security (Docker Isolation):** Code runs in an ephemeral Docker container, blocked from accessing the Host's filesystem, network, or sensitive resources.
  * **Performance (Sidecar Pattern):** The container is started only once (the *Sidecar* pattern) and reused via `docker exec`, eliminating Docker boot time latency.
  * **Dynamic Inputs:** Allows adding execution inputs (`*`, `STRING`, `INT`, etc.) dynamically via the context menu.
  * **Multiple Outputs:** Provides 6 result outputs (`r1` to `r6`) and 1 log output (`log`).
  * **Non-Root Execution:** Code runs as the **`nobody`** user inside the container, significantly minimizing internal security risk.

-----

## Installation

### 1\. Mandatory Prerequisites

You must have two pieces of software installed:

  * **Docker Desktop/Engine:** The containerization engine itself.
  * **`docker-py`:** The Python library to control Docker.

Execute the following command in your ComfyUI Python environment:

```bash
# Installs the Python library required to communicate with the Docker daemon
pip install docker
```

### 2\. Node Installation

1.  Clone this repository into your ComfyUI's `custom_nodes` folder:
    ```bash
    cd path/to/ComfyUI/custom_nodes/
    git clone [Your Repository URL]
    ```
2.  Restart ComfyUI.

-----

## Docker Engine Installation (Detailed CLI Instructions)

You must install and start the Docker service (Daemon) before using the node. **Note:** After installation, ensure your user is added to the `docker` group to run commands without `sudo` (e.g., `sudo usermod -aG docker $USER`).

| OS / Distribution | Installation Command Set (Root/Sudo Required) | Verification & Service |
| :--- | :--- | :--- |
| **Ubuntu/Debian** | **1. Install Prerequisites:**<br>`sudo apt update && sudo apt install ca-certificates curl gnupg`<br>**2. Add GPG Key:**<br>`sudo install -m 0755 -d /etc/apt/keyrings`<br>`curl -fsSL https://download.docker.com/linux/ubuntu/gpg \| sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg`<br>**3. Add Repository:**<br>`echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" \| sudo tee /etc/apt/sources.list.d/docker.list > /dev/null`<br>**4. Install Docker:**<br>`sudo apt update && sudo apt install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin` | `sudo systemctl enable docker --now` |
| **Arch/Manjaro** | **1. Install Package:**<br>`sudo pacman -Syu docker`<br>**2. Start Service:**<br>`sudo systemctl start docker.service` | `sudo systemctl status docker.service` |
| **Fedora/RHEL** | **1. Install Package:**<br>`sudo dnf -y install docker-ce docker-ce-cli containerd.io --repo docker-ce --repo docker-ce-stable`<br>**2. Start Service:**<br>`sudo systemctl start docker` | `sudo systemctl enable docker --now` |
| **macOS** | **Install Docker Desktop (Recommended):** Download the official `.dmg` installer from the Docker website. | Start the application. CLI tools (`docker`) are installed automatically. |
| **Windows** | **Install Docker Desktop (Recommended):** Download the official installer from the Docker website.<br>**Prerequisite:** Ensure **WSL 2** is installed and enabled for optimal performance. | Start the application. Verify in PowerShell: `docker info` |

-----

### Clarification on Windows Installation

**WSL 2 and Windows:** Docker Desktop for Windows uses a lightweight Linux virtual machine (VM) powered by **WSL 2** by default. This VM hosts the Docker Engine. Therefore, while you install the *Desktop app*, you must have **WSL 2 enabled** for the container engine to function correctly and offer the best performance.

-----

## Usage Guide

### 1\. Add the Node

Find **"Docker Sandbox Runner"** in the **Advanced/Scripting** menu.

### 2\. Define Inputs

1.  **Code (`code`):** Insert your Python script. The desired outputs must be assigned to variables `r1` through `r6`.
2.  **Dynamic Inputs:** Right-click the node and use **"+ Add Input (Dynamic)"** to inject variables (e.g., `my_int (INT)`).

### 3\. Example Code

```python
# Access the injected variable "my_value" from the input slot
# Libraries like math, random, json, re, time are pre-loaded.

import math 

if my_value > 50:
    r1 = "Processed successfully."
    r2 = my_value * math.pi
else:
    r1 = "Value too low."
    r2 = None
```

### 4\. Resource Management

The persistent container `comfyui-sandbox-worker` will run until explicitly stopped.

  * **To Stop Consumption:** Stop the container manually via the Docker Desktop GUI or by CLI:
    ```bash
    docker stop comfyui-sandbox-worker
    ```

-----

## License

This project is licensed under the **MIT License**.

```
MIT License

Copyright (c) 2025 [Your Name or Project Name]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

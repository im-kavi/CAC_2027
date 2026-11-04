#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALLER_DIR="${SCRIPT_DIR}/zed_sdk"
mkdir -p "${INSTALLER_DIR}"
INSTALLER=$(find "${INSTALLER_DIR}" -maxdepth 1 -name "ZED_SDK_*.run" | head -n 1)

if [ -z "${INSTALLER}" ]; then
    echo "No ZED SDK installer found in ${INSTALLER_DIR}."
    echo "Downloading compatible ZED SDK 5.5 (Ubuntu 24.04 / CUDA 12)..."
    INSTALLER="${INSTALLER_DIR}/ZED_SDK_Ubuntu24_cuda12.8_tensorrt10.9_v5.5.1.zstd.run"
    wget -c --progress=dot:giga "https://download.stereolabs.com/zedsdk/5.5/cu12_trt10/ubuntu24" -O "${INSTALLER}"
fi

echo "=========================================================="
echo "Installing Stereolabs ZED SDK"
echo "Installer: ${INSTALLER}"
echo "=========================================================="

chmod +x "${INSTALLER}"

# Check for silent argument or interactive
if [ "$1" == "--silent" ] || [ "$1" == "silent" ]; then
    echo "Running unattended silent installation..."
    "${INSTALLER}" -- silent
else
    echo "Running interactive installer (you can review license & options)..."
    echo "To run unattended in the future, pass: ./install_zed_sdk.sh --silent"
    "${INSTALLER}"
fi

echo "=========================================================="
echo "ZED SDK Installation completed."
echo "You can now run './build_ws.sh' to compile the ROS 2 wrapper!"
echo "=========================================================="

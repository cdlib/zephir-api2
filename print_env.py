#!/usr/bin/env python3

import os
import subprocess

def get_os_info():
    os_info = {}
    with open("/etc/os-release") as f:
        for line in f:
            if "=" in line:
                key, value = line.strip().split("=", 1)
                os_info[key] = value.strip('"')
    return os_info

def get_debian_version():
    try:
        with open("/etc/debian_version") as f:
            return f.read().strip()
    except FileNotFoundError:
        return "Unknown"

def get_python_version():
    result = subprocess.run(["python", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return result.stdout.decode().strip() or result.stderr.decode().strip()

def main():
    os_info = get_os_info()
    debian_version = get_debian_version()
    python_version = get_python_version()

    print("--------ENVIRONMENT OUTPUT--------")
    print(f"ENV_OUTPUT_ID: {os_info.get('ID', 'Unknown')}")
    print(f"ENV_OUTPUT_VERSION_ID: {os_info.get('VERSION_ID', 'Unknown')}")
    print(f"ENV_OUTPUT_VERSION_CODENAME: {os_info.get('VERSION_CODENAME', 'Unknown')}")
    print(f"ENV_OUTPUT_FULL_VERSION: {debian_version}")
    print(f"ENV_OUTPUT_LANGUAGE_VERSION: {python_version}")
    print("--------ENVIRONMENT OUTPUT--------")

if __name__ == "__main__":
    main()

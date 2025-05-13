#!/usr/bin/env python3
"""
Setup script for the DEV.to posting service.
This script:
1. Installs required packages
2. Creates a .env file for the API key
3. Sets up the service to run in the background
"""

import os
import sys
import subprocess
import platform
import getpass

def install_requirements():
    """Install required packages"""
    print("Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Packages installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install packages: {e}")
        return False

def setup_env_file():
    """Set up the .env file with the DEV.to API key"""
    if os.path.exists(".env"):
        with open(".env", "r") as f:
            content = f.read()
            if "DEV_TO_API_KEY" in content:
                print("✅ DEV_TO_API_KEY already exists in .env file")
                return True
    
    api_key = input("Enter your DEV.to API key: ").strip()
    if not api_key:
        print("❌ API key is required")
        return False
    
    with open(".env", "a") as f:
        f.write(f"\nDEV_TO_API_KEY={api_key}\n")
    
    print("✅ API key added to .env file")
    return True

def setup_windows_service():
    """Set up the service on Windows using Task Scheduler"""
    print("Setting up Windows Task Scheduler job...")
    
    # Get the current directory and script path
    current_dir = os.path.abspath(os.path.dirname(__file__))
    script_path = os.path.join(current_dir, "post_to_dev.py")
    python_path = sys.executable
    
    # Create a batch file to run the script
    batch_file = os.path.join(current_dir, "run_dev_poster.bat")
    with open(batch_file, "w") as f:
        f.write(f'@echo off\n')
        f.write(f'cd /d "{current_dir}"\n')
        f.write(f'"{python_path}" "{script_path}"\n')
    
    # Create the task scheduler command
    task_name = "DEVtoPostingService"
    command = [
        "schtasks", "/create", "/tn", task_name, "/tr", batch_file,
        "/sc", "onstart", "/ru", os.environ["USERNAME"],
        "/f"  # Force creation/overwrite
    ]
    
    try:
        subprocess.check_call(command)
        print(f"✅ Windows Task Scheduler job '{task_name}' created successfully")
        print(f"   The service will start automatically when you log in")
        print(f"   To start it now, run: schtasks /run /tn {task_name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create Windows Task Scheduler job: {e}")
        print("You can manually set up the task to run the batch file at startup")
        return False

def setup_linux_service():
    """Set up the service on Linux using systemd"""
    print("Setting up Linux systemd service...")
    
    # Get the current directory and script path
    current_dir = os.path.abspath(os.path.dirname(__file__))
    script_path = os.path.join(current_dir, "post_to_dev.py")
    python_path = sys.executable
    
    # Create the systemd service file
    service_name = "dev-to-poster"
    service_file = f"{service_name}.service"
    service_path = os.path.join(os.path.expanduser("~"), ".config", "systemd", "user")
    
    # Create the directory if it doesn't exist
    os.makedirs(service_path, exist_ok=True)
    
    service_content = f"""[Unit]
Description=DEV.to Blog Post Scheduler
After=network.target

[Service]
Type=simple
WorkingDirectory={current_dir}
ExecStart={python_path} {script_path}
Restart=always
RestartSec=10

[Install]
WantedBy=default.target
"""
    
    service_file_path = os.path.join(service_path, service_file)
    with open(service_file_path, "w") as f:
        f.write(service_content)
    
    # Make the script executable
    os.chmod(script_path, 0o755)
    
    # Enable and start the service
    try:
        subprocess.check_call(["systemctl", "--user", "daemon-reload"])
        subprocess.check_call(["systemctl", "--user", "enable", service_name])
        subprocess.check_call(["systemctl", "--user", "start", service_name])
        
        print(f"✅ Linux systemd service '{service_name}' created and started")
        print(f"   To check status: systemctl --user status {service_name}")
        print(f"   To stop: systemctl --user stop {service_name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to set up Linux service: {e}")
        print("You can manually set up the service using the created service file")
        return False

def setup_macos_service():
    """Set up the service on macOS using launchd"""
    print("Setting up macOS launchd service...")
    
    # Get the current directory and script path
    current_dir = os.path.abspath(os.path.dirname(__file__))
    script_path = os.path.join(current_dir, "post_to_dev.py")
    python_path = sys.executable
    
    # Create the launchd plist file
    service_name = "com.revisepdf.devposter"
    plist_file = f"{service_name}.plist"
    launch_agents_dir = os.path.join(os.path.expanduser("~"), "Library", "LaunchAgents")
    
    # Create the directory if it doesn't exist
    os.makedirs(launch_agents_dir, exist_ok=True)
    
    plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>{service_name}</string>
    <key>ProgramArguments</key>
    <array>
        <string>{python_path}</string>
        <string>{script_path}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>WorkingDirectory</key>
    <string>{current_dir}</string>
    <key>StandardErrorPath</key>
    <string>{current_dir}/dev_poster_error.log</string>
    <key>StandardOutPath</key>
    <string>{current_dir}/dev_poster_output.log</string>
</dict>
</plist>
"""
    
    plist_file_path = os.path.join(launch_agents_dir, plist_file)
    with open(plist_file_path, "w") as f:
        f.write(plist_content)
    
    # Make the script executable
    os.chmod(script_path, 0o755)
    
    # Load the service
    try:
        subprocess.check_call(["launchctl", "load", plist_file_path])
        
        print(f"✅ macOS launchd service '{service_name}' created and loaded")
        print(f"   To check status: launchctl list | grep {service_name}")
        print(f"   To stop: launchctl unload {plist_file_path}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to set up macOS service: {e}")
        print("You can manually load the service using: launchctl load", plist_file_path)
        return False

def main():
    """Main setup function"""
    print("Setting up DEV.to posting service...")
    
    # Install required packages
    if not install_requirements():
        print("Failed to install required packages. Exiting.")
        return
    
    # Set up the .env file
    if not setup_env_file():
        print("Failed to set up .env file. Exiting.")
        return
    
    # Set up the service based on the operating system
    system = platform.system()
    if system == "Windows":
        setup_windows_service()
    elif system == "Linux":
        setup_linux_service()
    elif system == "Darwin":  # macOS
        setup_macos_service()
    else:
        print(f"Unsupported operating system: {system}")
        print("Please set up the service manually.")
    
    print("\nSetup complete!")
    print("The service will post to DEV.to according to the schedule in the configuration.")
    print("You can modify the schedule by editing the dev_posting_config.json file.")

if __name__ == "__main__":
    main()

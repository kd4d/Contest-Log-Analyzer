Installing Docker on Windows 11 is best achieved by using **Docker Desktop** with the **WSL 2** (Windows Subsystem for Linux) backend. This method offers the best performance and compatibility compared to the legacy Hyper-V backend.

Here is the step-by-step guide to installing Docker on Windows 11.

### **Prerequisites**

Before starting, ensure your system meets these requirements:

  * **OS:** Windows 11 64-bit (Home, Pro, Enterprise, or Education).
  * **Hardware:** 64-bit processor with Second Level Address Translation (SLAT), 4GB RAM, and Virtualization enabled in BIOS/UEFI.

-----

### **Step 1: Enable WSL 2 (Recommended)**

While Docker Desktop can try to configure this for you, it is cleaner to enable it manually first to ensure the Linux kernel is ready.

1.  Open **PowerShell** or **Command Prompt** as Administrator.
2.  Run the following command to install the Windows Subsystem for Linux and the default Ubuntu distribution:
    ```powershell
    wsl --install
    ```
      * *Note: If you already have WSL installed, run `wsl --update` to ensure you have the latest kernel.*
3.  **Restart your computer** when prompted to complete the installation.

-----

### **Step 2: Install Docker Desktop**

1.  **Download the Installer:**
    Go to the official [Docker Desktop for Windows page](https://www.docker.com/products/docker-desktop/) and download the installer ("Docker Desktop Installer.exe").

2.  **Run the Installer:**
    Double-click the `.exe` file to start the installation.

3.  **Configuration:**

      * When prompted, ensure the option **"Use WSL 2 instead of Hyper-V"** (or "Install required Windows components for WSL 2") is checked. This is usually selected by default and is the recommended setting.
      * 
4.  **Finish Installation:**
    Follow the on-screen instructions. Once complete, you may be asked to **Log out and log back in** or restart your computer for the changes to take effect.

-----

### **Step 3: Start and Verify Docker**

1.  **Launch Docker Desktop:**
    Open the "Docker Desktop" application from your Start menu. It may take a minute to initialize the Docker Engine.

      * *Note: You may be prompted to accept the Docker Subscription Service Agreement.*

2.  **Verify via Terminal:**
    Open PowerShell or Command Prompt and type the following command to check the installed version:

    ```powershell
    docker --version
    ```

3.  **Run a Test Container:**
    To confirm everything is working correctly, run the standard "Hello World" container:

    ```powershell
    docker run hello-world
    ```

    If successful, you will see a message saying "Hello from Docker\! This message shows that your installation appears to be working correctly."

-----

### **Troubleshooting**

  * **Virtualization Not Enabled:** If Docker fails to start, check your Task Manager (**Ctrl + Shift + Esc** \> **Performance** \> **CPU**) to see if "Virtualization" is set to "Enabled". If not, you must enable it in your computer's BIOS/UEFI settings.
  * **WSL Kernel Update:** If you receive an error regarding the WSL kernel, run `wsl --update` in an administrator PowerShell terminal.
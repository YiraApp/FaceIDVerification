# Installing Microsoft Visual Studio Build Tools for InsightFace

## Why Do You Need This?

InsightFace requires C++ compilation tools to install on Windows. The easiest way to get these is by installing Microsoft's free Build Tools.

## Step-by-Step Installation Guide

### Step 1: Download Build Tools

**Option A - Direct Download:**
1. Click this link: https://visualstudio.microsoft.com/visual-cpp-build-tools/
2. Click the **"Download Build Tools"** button
3. Save the file (vs_BuildTools.exe)

**Option B - Full Visual Studio (if you want the IDE too):**
1. Download Visual Studio Community: https://visualstudio.microsoft.com/vs/community/
2. This includes Build Tools + a full IDE

### Step 2: Run the Installer

1. **Run** the downloaded `vs_BuildTools.exe`
2. The Visual Studio Installer will open
3. Wait for it to initialize

### Step 3: Select Workload

In the installer window:

1. Check the box for **"Desktop development with C++"**
   
   This will install:
   - MSVC v143 - VS 2022 C++ x64/x86 build tools
   - Windows 10/11 SDK
   - C++ CMake tools
   - Testing tools

2. (Optional) On the right side, you can uncheck components you don't need to save space

3. Click **"Install"** button at the bottom right

### Step 4: Wait for Installation

- **Size:** ~7 GB download
- **Time:** 10-30 minutes depending on your internet speed
- **Disk Space Required:** ~10 GB

The installer will:
- Download required components
- Install them
- Configure your system

### Step 5: Restart Your Computer (Recommended)

After installation completes, restart your computer to ensure all environment variables are set correctly.

### Step 6: Install InsightFace

1. **Open a NEW PowerShell/Command Prompt** (important - must be new to pick up new environment variables)

2. Navigate to your project:
   ```bash
   cd "c:\Users\PAC-LAP\VSC Repo\FaceIDAPI"
   ```

3. Install InsightFace:
   ```bash
   pip install insightface
   ```

4. This should now work! You'll see compilation messages as it builds.

### Step 7: Verify Installation

```bash
python -c "from insightface.app import FaceAnalysis; print('✅ InsightFace installed successfully!')"
```

If you see the success message, you're done!

## Alternative: Minimal Installation

If you don't want the full Build Tools, you can try installing just the essentials:

1. **Install Windows SDK only:**
   - Download: https://developer.microsoft.com/en-us/windows/downloads/windows-sdk/
   - Install with default options

2. **Try pip install again:**
   ```bash
   pip install insightface
   ```

This might work, but Build Tools is more reliable.

## Troubleshooting

### "Still getting errors after installing Build Tools"

1. Make sure you **restarted your terminal** (or computer)
2. Verify Build Tools are installed:
   ```bash
   where cl
   ```
   This should show the path to the C++ compiler

3. Try installing with verbose output:
   ```bash
   pip install insightface -v
   ```

### "Don't have 10GB of space"

Consider using Docker instead:
1. Install Docker Desktop for Windows
2. Use a Linux-based container where InsightFace installs easily
3. See `README.md` for Docker instructions

## After InsightFace is Installed

Start your FastAPI server:

```bash
uvicorn app.main:app --reload
```

Then open: http://localhost:8000/docs

Test the `/api/verify-face` endpoint with a PDF containing ID + selfie!

---

## Quick Reference

| Step | Action | Time |
|------|--------|------|
| 1 | Download Build Tools | 2 min |
| 2 | Install Build Tools | 15-30 min |
| 3 | Restart computer | 2 min |
| 4 | `pip install insightface` | 3-5 min |
| 5 | Test & run server | 1 min |

**Total Time:** ~30-45 minutes (mostly waiting for downloads/installation)

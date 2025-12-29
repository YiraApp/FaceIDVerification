# InsightFace Installation Guide for Windows

## Problem
InsightFace requires Microsoft Visual C++ 14.0+ to build from source, which causes installation failures on Windows.

## Solutions (Choose ONE)

### ✅ **Option 1: Use Conda (EASIEST - Recommended)**

Since you have Anaconda installed, this is the simplest approach:

```bash
# Install insightface via conda-forge
conda install -c conda-forge insightface -y
```

**Pros:**
- No need to install C++ Build Tools
- Pre-compiled binaries
- Fast installation

**Cons:**
- Requires Anaconda/Miniconda

---

### ✅ **Option 2: Install Microsoft C++ Build Tools**

1. **Download Build Tools:**
   - Visit: https://visualstudio.microsoft.com/visual-cpp-build-tools/
   - Download "Build Tools for Visual Studio 2022"

2. **Install with C++ workload:**
   - Run the installer
   - Select "Desktop development with C++"
   - Click Install (requires ~7GB disk space)

3. **Restart terminal and install:**
   ```bash
   pip install insightface
   ```

**Pros:**
- Works with pip/venv
- Good for production deployments

**Cons:**
- Large download (~7GB)
- Takes time to install

---

### ✅ **Option 3: Use Pre-built Wheel (FASTEST)**

Download a pre-built wheel file:

1. **Visit:** https://www.lfd.uci.edu/~gohlke/pythonlibs/#insightface
   (Or search for "insightface windows wheel python 3.13")

2. **Download the appropriate .whl file** for your Python version:
   - Example: `insightface-0.7.3-cp313-cp313-win_amd64.whl` (for Python 3.13)

3. **Install the wheel:**
   ```bash
   pip install path\to\downloaded\insightface-0.7.3-cp313-cp313-win_amd64.whl
   ```

**Pros:**
- No C++ Build Tools needed
- Fast installation

**Cons:**
- Need to find compatible wheel
- May not be available for latest Python versions

---

### ✅ **Option 4: Use Docker (For deployment)**

If you're deploying to production, consider using Docker with a Linux base image:

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## Recommended Approach

**For Development (Windows):**
```bash
conda install -c conda-forge insightface -y
```

**For Production (Linux/Docker):**
```bash
pip install insightface
```

---

## After Installing InsightFace

Once installed, verify it works:

```bash
python -c "from insightface.app import FaceAnalysis; print('InsightFace installed successfully!')"
```

Then start the FastAPI server:

```bash
uvicorn app.main:app --reload
```

Visit: http://localhost:8000/docs

---

## Current Status

All other dependencies are already installed:
✅ FastAPI
✅ Uvicorn
✅ OpenCV
✅ ONNX Runtime
✅ PyMuPDF
✅ Pydantic
✅ NumPy

Only InsightFace is pending!

# SESAME EoS GUI Analysis Tool

<div align="center">

[![English](https://img.shields.io/badge/Language-English-blue.svg)](README.md)
[![中文](https://img.shields.io/badge/语言-中文-red.svg)](README_CN.md)

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![Platform](https://img.shields.io/badge/platform-windows%20%7C%20macOS%20%7C%20linux-lightgrey)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Version](https://img.shields.io/badge/version-2.2.1-blue.svg)

**A standalone GUI application for analyzing SESAME equation of state (EoS) data files**

</div>

## ✨ Key Features

### 🔧 **Ready to Use**
- **Automatic Dependency Management**: No manual installation of complex dependencies, program automatically handles opacplot2 and hedp installation
- **Smart Installation**: Automatically handles Cython version compatibility issues
- **Cross-Platform Support**: Universal for Windows, macOS, and Linux

### 📊 **SESAME File Analysis**
- Load and analyze SESAME format files (.ses)
- Automatically detect material ID and basic properties
- Support for single and double precision formats
- Generate comprehensive material property reports

### 📈 **Data Visualization**
- **Density-Temperature Grid**: Interactive grid point distribution plots
- **Internal Energy Analysis**: Contour plots with automatic positive internal energy temperature detection
- **Pressure Analysis**: Pressure distribution visualization
- Support for different EoS types (total, electron, ion, etc.)
- Export charts in PNG, PDF, SVG formats

### 🔄 **Format Conversion (Enhanced in v2.2.0)**
- **Precise Conversion**: Convert SESAME files to CN4/IONMIX format
- **Ion Density Grid**: Direct use of opacplot2's native ion number density data
- **100% Accuracy**: Completely consistent with original opac-convert command output
- **Parameter Validation**: Smart parameter validation and suggestions
- **Real-time Progress**: Visual display of conversion process

## 🚀 Quick Start

### Method 1: Using Launcher (Recommended)
```bash
git clone <your-repo-url>
cd sesame-eos-gui
python launch.py
```

The launcher will:
1. Automatically check dependencies
2. Automatically install opacplot2 and hedp if needed
3. Launch the GUI interface

### Method 2: Manual Installation
```bash
git clone <your-repo-url>
cd sesame-eos-gui

# Install dependencies
python setup.py

# Launch GUI
python main.py
```

## 📋 System Requirements

- Python 3.8 or higher
- Internet connection (for dependency installation on first run)
- Operating System: Windows, macOS, Linux

## 📖 User Guide

### 1. **Load SESAME File**
- Click the "Load SES File" button
- Select a SESAME file in .ses format
- The program automatically analyzes and displays basic information

### 2. **View Material Report**
- Switch to the "Material Report" tab
- Click "Generate Report" to view detailed analysis
- Save the report as a text file

### 3. **Visualize Density-Temperature Grid**
- Switch to the "D-T Grid Visualization" tab
- Select EoS type (total, electron, ion, etc.)
- Click "Generate Plot" to create visualization charts
- Support for multiple export formats

### 4. **Analyze Internal Energy Distribution**
- Switch to the "Internal Energy Analysis" tab
- Select EoS type
- Click "Analyze & Plot" to perform analysis
- View minimum positive internal energy temperature

### 5. **Convert File Format**
- Switch to the "SES to CN4 Conversion" tab
- Configure conversion parameters (atomic number, fractions, etc.)
- Click "Load Suggested Parameters" for automatic suggestions
- Click "Convert to CN4" to execute conversion

## 🔧 Dependency Management

The program automatically manages the following dependencies:

### Core Dependencies
- `opacplot2`: SESAME data processing library
- `hedp`: High Energy Density Physics package
- `numpy`, `scipy`, `matplotlib`: Scientific computing libraries

### Important Notes
- The program automatically installs `cython<3.0` to ensure hedp compatibility
- First run may take a few minutes to install dependencies
- Installation process displays progress information

## 🗂️ Project Structure

```
sesame-eos-gui/
├── main.py              # Main GUI application
├── launch.py            # Launcher script
├── setup.py             # Dependency installation script
├── requirements.txt     # Python package dependencies
├── sesame_analyzer.py   # SESAME data analysis module
├── opac_converter.py    # Format conversion module
└── README.md           # User documentation
```

## ⚠️ Troubleshooting

### Common Issues

1. **Dependency Installation Failed**
   ```bash
   # Manual installation
   python setup.py
   ```

2. **Cython Version Issues**
   ```bash
   pip uninstall cython -y
   pip install "cython<3.0"
   ```

3. **opacplot2 Installation Failed**
   ```bash
   pip install git+https://github.com/flash-center/opacplot2.git
   ```

4. **hedp Installation Failed**
   ```bash
   pip install "cython<3.0"
   pip install git+https://github.com/luli/hedp.git
   ```

### Getting Help

If you encounter problems, please check:
1. Python version is >=3.8
2. Internet connection is working
3. Sufficient disk space available
4. Terminal/command prompt permissions

## 📝 Changelog

### v2.2.1 (2025-08)
- **🎨 Major Pressure Analysis Enhancement**: Three-layer rendering strategy eliminates white boundary artifacts
- **🔴 Negative Region Optimization**: Gray background for all non-positive pressure areas (P ≤ 0)
- **📈 Logarithmic Positive Display**: nipy_spectral colormap with optimized logarithmic scaling
- **📊 Professional Colorbar**: True 10^x exponential format (replacing 1e+08) with 12 tick marks
- **🔄 Smart EoS Ordering**: Priority adjusted to ioncc > ele > ion > total for better defaults
- **🏷️ P=0 Contour Lines**: Black dashed lines marking zero-pressure boundaries

### v2.2.0 (2024-08)
- **🎯 Core Fix**: Major improvement to format conversion functionality
- **✅ Precise Conversion**: Direct use of `eos_dict['idens']` as ion number density grid
- **🔧 Code Optimization**: Removed manual density conversion logic, reduced 81 lines of code (-20%)
- **📊 100% Accuracy**: Completely consistent with opac-convert command output (binary-level matching)
- **🎨 Principle Adherence**: Strict refactoring according to KISS, DRY, SRP software engineering principles
- **📋 Complete Validation**: Added benchmark testing tools to ensure conversion correctness

### v2.1.1
- Improved error handling for conversion functionality
- Optimized user interface responsiveness

### v2.0
- Rewritten as standalone application, no need to install in opacplot2 directory
- Automatic dependency management
- Improved user interface
- Better error handling

### v1.0
- Initial version
- Basic SESAME file analysis functionality

## 🤝 Contributing

Welcome to submit issue reports and feature suggestions!

## 📄 License

MIT License - See LICENSE file for details

---

**Get Started: Run `python launch.py` to begin!**
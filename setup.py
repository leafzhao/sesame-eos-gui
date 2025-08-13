#!/usr/bin/env python3
"""
SESAME EoS GUI Setup Script
Automatically installs opacplot2 and hedp dependencies
"""

import subprocess
import sys
import os
import importlib.util

def check_module_installed(module_name):
    """Check if a module is already installed"""
    return importlib.util.find_spec(module_name) is not None

def run_command(cmd, description, critical=True):
    """Run a command and handle errors"""
    print(f"\n📦 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
        print(f"✅ {description} completed successfully")
        if result.stdout and len(result.stdout.strip()) > 0:
            # Show first 200 chars of output to avoid spam
            output_preview = result.stdout.strip()[:200]
            if len(result.stdout) > 200:
                output_preview += "..."
            print("Output:", output_preview)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        if e.stderr:
            print("Error:", e.stderr.strip())
        if critical:
            return False
        else:
            print("⚠️ Non-critical failure, continuing...")
            return True

def check_module_functionality(module_name):
    """Check if a module is installed AND functional"""
    try:
        if module_name == 'opacplot2':
            import opacplot2
            return True, opacplot2.__version__
        elif module_name == 'hedp':
            import hedp
            return True, hedp.__version__
        else:
            module = importlib.import_module(module_name)
            version = getattr(module, '__version__', 'unknown')
            return True, version
    except ImportError as e:
        return False, f"Import error: {e}"
    except Exception as e:
        return False, f"Compatibility issue: {e}"

def install_dependencies():
    """Install all required dependencies for the GUI"""
    print("🚀 SESAME EoS GUI Dependency Installer")
    print("=" * 50)
    
    # Check current installation status with functionality test
    opacplot2_ok, opacplot2_status = check_module_functionality('opacplot2')
    hedp_ok, hedp_status = check_module_functionality('hedp')
    
    print(f"\nCurrent dependency status:")
    if opacplot2_ok:
        print(f"  opacplot2: ✅ v{opacplot2_status} (functional)")
    else:
        print(f"  opacplot2: ❌ {opacplot2_status}")
    
    if hedp_ok:
        print(f"  hedp: ✅ v{hedp_status} (functional)")
    else:
        print(f"  hedp: ⚠️  {hedp_status}")
    
    # Determine what needs to be done
    needs_opacplot2 = not opacplot2_ok
    needs_hedp = not hedp_ok
    
    if opacplot2_ok and not needs_hedp:
        print("\n🎉 All major dependencies are functional!")
        print("Installing/updating supporting libraries...")
    elif opacplot2_ok and needs_hedp:
        print("\n🎯 opacplot2 is working fine!")
        print("⚠️  hedp has compatibility issues (will provide alternative solution)")
        print("Installing/updating supporting libraries...")
    else:
        print(f"\n🔧 Installing missing dependencies...")
    
    # Step 1: Install basic requirements from requirements.txt
    if not run_command('pip install -r requirements.txt', "Installing basic requirements", critical=False):
        print("⚠️  Some basic requirements failed to install, trying individual installation...")
        
        # Try installing key packages individually
        basic_packages = ['numpy', 'scipy', 'matplotlib', 'tables', 'numba', 'pandas']
        for pkg in basic_packages:
            run_command(f'pip install {pkg}', f"Installing {pkg}", critical=False)
    
    # Step 2: Install opacplot2 if missing
    if needs_opacplot2:
        print("\n📥 Installing opacplot2 from GitHub...")
        if not run_command('pip install git+https://github.com/flash-center/opacplot2.git', 
                          "Installing opacplot2"):
            print("❌ CRITICAL: Failed to install opacplot2. GUI will not function.")
            return False
        print("✅ opacplot2 installed successfully")
    
    # Step 3: Handle hedp installation/compatibility
    if needs_hedp:
        print("\n📥 Attempting to install/fix hedp...")
        
        # First try to fix scipy compatibility
        print("🔧 Checking scipy version compatibility...")
        scipy_needs_downgrade = False
        try:
            import scipy
            scipy_version = scipy.__version__
            print(f"📋 Current scipy version: {scipy_version}")
            
            # Check if scipy version is too new for hedp
            major_version = int(scipy_version.split('.')[0])
            minor_version = int(scipy_version.split('.')[1])
            
            if major_version > 1 or (major_version == 1 and minor_version >= 14):
                print("⚠️  scipy version too new for hedp compatibility")
                print("🔧 Downgrading scipy to <=1.13.0 for hedp compatibility...")
                scipy_needs_downgrade = True
            else:
                print(f"✅ scipy version {scipy_version} should be compatible with hedp")
            
        except ImportError:
            print("📋 scipy not found, will install compatible version with hedp")
            scipy_needs_downgrade = True
        
        # Try Cython version fix
        try:
            import Cython
            cython_version = Cython.__version__
            major_version = int(cython_version.split('.')[0])
            if major_version >= 3:
                print("🔧 Downgrading Cython for hedp compatibility...")
                run_command('pip install "cython<3.0"', "Installing compatible Cython", critical=False)
        except ImportError:
            print("📋 Installing Cython for hedp...")
            run_command('pip install "cython<3.0"', "Installing Cython < 3.0", critical=False)
        
        # Install compatible scipy version if needed
        if scipy_needs_downgrade:
            scipy_downgrade_success = run_command('pip install "scipy<=1.13.0"', 
                                                 "Downgrading scipy for hedp compatibility", critical=False)
            if not scipy_downgrade_success:
                print("⚠️  Failed to downgrade scipy, hedp may not work properly")
        
        # Attempt hedp installation
        hedp_installed = run_command('pip install git+https://github.com/luli/hedp.git', 
                                    "Installing hedp", critical=False)
        
        if not hedp_installed:
            print("⚠️  hedp installation failed, but this won't prevent GUI from working")
            print("💡 GUI will provide alternative solution for format conversion")
    
    # Verification step - focus on critical components
    print("\n🔍 Verifying critical components...")
    
    # Check opacplot2 (critical)
    opacplot2_final_ok, opacplot2_final_status = check_module_functionality('opacplot2')
    if opacplot2_final_ok:
        print(f"✅ opacplot2 v{opacplot2_final_status} - CRITICAL component working")
        critical_success = True
    else:
        print(f"❌ opacplot2 - CRITICAL component failed: {opacplot2_final_status}")
        critical_success = False
    
    # Check hedp (nice-to-have, but not critical for basic GUI functionality)  
    hedp_final_ok, hedp_final_status = check_module_functionality('hedp')
    if hedp_final_ok:
        print(f"✅ hedp v{hedp_final_status} - Format conversion available")
        conversion_available = True
    else:
        print(f"⚠️  hedp - Format conversion limited: {hedp_final_status}")
        # Even if hedp has issues, opacplot2 can still do conversion
        conversion_available = opacplot2_final_ok  # Updated logic
    
    # Test opacplot2 functionality if available
    if opacplot2_final_ok:
        try:
            import opacplot2.convert_opl
            print("✅ opacplot2 conversion modules accessible")
        except Exception as e:
            print(f"⚠️  opacplot2 conversion module warning: {e}")
    
    # Final assessment
    if critical_success:
        if conversion_available:
            print("\n🎉 Installation completed successfully!")
            print("✅ Full functionality available (SESAME analysis + format conversion)")
        else:
            print("\n🎯 Installation mostly successful!")
            print("✅ SESAME analysis fully functional")
            print("⚠️  Format conversion has limitations (hedp compatibility issues)")
            print("💡 Alternative conversion methods will be provided in GUI")
        
        print("\n🚀 You can now run the GUI with:")
        print("  python main.py")
        print("  or")
        print("  python launch.py")
        return True
    else:
        print("\n❌ Critical installation failure!")
        print("opacplot2 is required for basic GUI functionality.")
        print("\n🔧 Please try:")
        print("1. Check internet connection")
        print("2. Run: pip install git+https://github.com/flash-center/opacplot2.git")
        print("3. Then restart the GUI")
        return False

if __name__ == "__main__":
    success = install_dependencies()
    
    if not success:
        print("\n❌ Setup encountered errors. Please:")
        print("1. Check your internet connection")
        print("2. Ensure you have pip installed and working")
        print("3. Try running individual install commands manually")
        print("4. Check the error messages above for specific issues")
        sys.exit(1)
    else:
        print("\n✅ Setup completed successfully!")
        sys.exit(0)
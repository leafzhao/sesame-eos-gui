#!/usr/bin/env python3
"""
SESAME EoS GUI Launcher
Convenient launcher script that handles dependencies and launches the GUI
"""

import sys
import os
import subprocess

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
            module = __import__(module_name)
            version = getattr(module, '__version__', 'unknown')
            return True, version
    except ImportError as e:
        return False, f"Import error: {e}"
    except Exception as e:
        return False, f"Compatibility issue: {e}"

def ensure_dependencies():
    """Ensure all dependencies are available"""
    print("SESAME EoS GUI Launcher")
    print("=" * 30)
    
    # Check opacplot2 (critical)
    opacplot2_ok, opacplot2_status = check_module_functionality('opacplot2')
    if opacplot2_ok:
        print("✅ opacplot2 found")
        opacplot2_missing = False
    else:
        print("❌ opacplot2 missing (CRITICAL)")
        opacplot2_missing = True
    
    # Check hedp (nice-to-have for full functionality)
    hedp_ok, hedp_status = check_module_functionality('hedp')
    if hedp_ok:
        print("✅ hedp found")
        hedp_missing = False
    else:
        print("❌ hedp missing (CRITICAL - needed for format conversion)")
        hedp_missing = True
    
    # Check scientific libraries
    try:
        import numpy, matplotlib, scipy
        print("✅ Scientific libraries found")
        sci_libs_missing = False
    except ImportError:
        print("❌ Some scientific libraries missing (CRITICAL)")
        sci_libs_missing = True
    
    # Only consider opacplot2 and scientific libraries as truly critical
    # hedp is important but GUI can work without it in opacplot2-only mode
    critical_missing = opacplot2_missing or sci_libs_missing
    
    # If only hedp is missing and we've already attempted installation, don't loop
    if not critical_missing and hedp_missing:
        print("\n💡 Note: hedp is missing but opacplot2 is available.")
        print("   GUI will work in opacplot2-only mode with limited conversion functionality.")
        return True  # Allow to proceed
    
    return not critical_missing

def install_dependencies():
    """Install missing dependencies"""
    print("\n🔧 Some dependencies are missing.")
    print("Running automatic installation...")
    
    try:
        result = subprocess.run([sys.executable, 'setup.py'], check=True)
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Installation failed: {e}")
        print("\nPlease try running manually:")
        print("  python setup.py")
        return False

def launch_gui():
    """Launch the main GUI application"""
    try:
        from main import main
        print("\n🚀 Launching SESAME EoS GUI...")
        main()
    except Exception as e:
        print(f"❌ Failed to launch GUI: {e}")
        print("\nTry running directly:")
        print("  python main.py")
        sys.exit(1)

def main():
    """Main launcher function"""
    # Change to script directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Check if we've been restarted (to avoid infinite loops)
    import sys
    restart_marker = '--after-install'
    restarted = restart_marker in sys.argv
    
    if restarted:
        print("\n🔄 Checking dependencies after installation...")
        sys.argv.remove(restart_marker)  # Clean up argv
    
    # Check dependencies
    if ensure_dependencies():
        print("\n✅ All dependencies found!")
        launch_gui()
    else:
        if restarted:
            # We've already tried installation, don't loop
            print("\n💡 Installation completed, but some dependencies still have issues.")
            print("\nThe GUI will work in limited mode (opacplot2-only for conversion).")
            print("\nOptions:")
            print("  y/yes - Start GUI anyway")
            print("  n/no  - Exit and install manually")
            
            response = input("\nYour choice (y/n): ").lower().strip()
            if response in ['y', 'yes']:
                print("\n🚀 Starting GUI in opacplot2-only mode...")
                launch_gui()
            else:
                print("\nTo fix remaining issues manually:")
                print("  pip install \"scipy<=1.13.0\"")
                print("  pip install git+https://github.com/luli/hedp.git")
                print("\nThen run: python main.py")
                sys.exit(0)
        else:
            # First time, offer installation
            print("\n⚠️  Missing dependencies detected.")
            print("\nOptions:")
            print("  y/yes - Install automatically")
            print("  n/no  - Skip installation and try to run anyway") 
            print("  q/quit - Exit")
            
            response = input("\nYour choice (y/n/q): ").lower().strip()
            
            if response in ['y', 'yes']:
                if install_dependencies():
                    print("\n🔄 Restarting with new dependencies...")
                    # Restart with marker to avoid infinite loops
                    os.execv(sys.executable, [sys.executable, __file__, restart_marker])
                else:
                    print("\n❌ Installation failed. Please install dependencies manually.")
                    print("You can also try running anyway with: python main.py")
                    sys.exit(1)
            elif response in ['n', 'no']:
                print("\n⚠️  Continuing with missing dependencies...")
                print("Some features may not work properly.")
                launch_gui()
            else:
                print("\nExiting. To install dependencies manually:")
                print("  python setup.py")
                print("\nThen run:")
                print("  python main.py")
                sys.exit(0)

if __name__ == "__main__":
    main()
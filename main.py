#!/usr/bin/env python3
"""
SESAME EoS GUI Application
Main application window with all functionality

A standalone GUI tool for analyzing SESAME equation of state (EoS) data files.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import os
import threading
import queue
import sys
import importlib.util

def check_dependencies():
    """Check for required dependencies and offer to install them"""
    missing_deps = []
    
    # Check for opacplot2 (required)
    try:
        import opacplot2
    except ImportError:
        missing_deps.append('opacplot2')
    
    # Check for hedp (required for SES to CN4 conversion)
    try:
        import hedp
    except ImportError:
        missing_deps.append('hedp')
    
    if missing_deps:
        root = tk.Tk()
        root.withdraw()  # Hide main window
        
        message = f"Missing required dependencies: {', '.join(missing_deps)}\n\n"
        message += "Options:\n\n"
        message += "• Click 'Yes' to install automatically\n"
        message += "• Click 'No' to skip installation and try to run anyway\n"
        message += "• Click 'Cancel' to exit\n\n"
        message += "Auto-install will add:\n"
        message += "• opacplot2 from GitHub\n"
        message += "• hedp from GitHub\n"
        message += "• Required scientific libraries\n\n"
        message += "Note: Some features may not work without missing dependencies."
        
        result = messagebox.askyesnocancel("Dependencies Missing", message)
        
        if result is True:  # Yes - install automatically
            try:
                # Try to run the setup
                import subprocess
                result = subprocess.run([sys.executable, 'setup.py'], capture_output=True, text=True)
                if result.returncode != 0:
                    messagebox.showerror("Installation Failed", 
                                       "Failed to install dependencies automatically.\n\n"
                                       "Please run: python setup.py\n\n"
                                       "You can also try running with missing dependencies by restarting the program and selecting 'No'.")
                    sys.exit(1)
                else:
                    messagebox.showinfo("Success", "Dependencies installed successfully!\nRestarting the application...")
                    # Restart the application
                    os.execv(sys.executable, [sys.executable] + sys.argv)
            except Exception as e:
                messagebox.showerror("Installation Error", 
                                   f"Failed to install dependencies: {str(e)}\n\n"
                                   "Please run: python setup.py\n\n"
                                   "You can also try running with missing dependencies by restarting the program and selecting 'No'.")
                sys.exit(1)
        elif result is False:  # No - skip installation and continue
            print("⚠️  Warning: Running with missing dependencies. Some features may not work.")
            print(f"Missing: {', '.join(missing_deps)}")
        else:  # Cancel - exit
            sys.exit(0)
        
        root.destroy()

# Check dependencies at startup
check_dependencies()

# Now import the modules (may have missing dependencies)
try:
    from sesame_analyzer import SESAMEAnalyzer
    from opac_converter import OPACConverter
except ImportError as e:
    print(f"⚠️  Warning: Failed to import some modules: {e}")
    print("Some features may not work properly.")
    # Create dummy classes to prevent crashes
    class SESAMEAnalyzer:
        def __init__(self):
            self.data_loaded = False
        def load_sesame_file(self, path):
            return False, "opacplot2 not available"
    
    class OPACConverter:
        def __init__(self):
            pass
        def validate_parameters(self, params):
            return ["opacplot2/hedp not available"]

class SESAMEAnalysisGUI:
    """Main GUI application class"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("SESAME EoS Analysis Tool v2.2.0")
        self.root.geometry("1200x800")
        
        # Initialize components
        self.analyzer = SESAMEAnalyzer()
        self.converter = OPACConverter()
        
        # GUI components
        self.notebook = None
        self.report_text = None
        self.progress_var = None
        self.status_label = None
        
        # Data storage
        self.current_file = None
        self.material_info = {}
        
        # Threading
        self.task_queue = queue.Queue()
        
        self.setup_gui()
        self.setup_menu()
        
    def setup_gui(self):
        """Setup the main GUI layout"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Top frame - File operations
        top_frame = ttk.LabelFrame(main_frame, text="File Operations", padding="10")
        top_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        top_frame.columnconfigure(1, weight=1)
        
        # File selection
        ttk.Button(top_frame, text="Load SES File", command=self.load_file).grid(row=0, column=0, padx=(0, 10))
        
        self.file_label = ttk.Label(top_frame, text="No file loaded")
        self.file_label.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        ttk.Button(top_frame, text="Reload", command=self.reload_file).grid(row=0, column=2, padx=(10, 0))
        
        # Notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Setup tabs
        self.setup_report_tab()
        self.setup_visualization_tab()
        self.setup_pressure_tab()
        self.setup_internal_energy_tab()
        self.setup_conversion_tab()
        
        # Bottom frame - Status
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        bottom_frame.columnconfigure(0, weight=1)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(bottom_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        self.status_label = ttk.Label(bottom_frame, text="Ready - Load a SES file to begin")
        self.status_label.grid(row=1, column=0, sticky=tk.W)
        
    def setup_menu(self):
        """Setup application menu"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Load SES File", command=self.load_file)
        file_menu.add_command(label="Reload", command=self.reload_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        
    def setup_report_tab(self):
        """Setup the report generation tab"""
        report_frame = ttk.Frame(self.notebook)
        self.notebook.add(report_frame, text="Material Report")
        
        report_frame.columnconfigure(0, weight=1)
        report_frame.rowconfigure(1, weight=1)
        
        # Controls
        controls_frame = ttk.Frame(report_frame)
        controls_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(controls_frame, text="Generate Report", command=self.generate_report).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(controls_frame, text="Save Report", command=self.save_report).grid(row=0, column=1)
        
        # Report text area
        self.report_text = scrolledtext.ScrolledText(report_frame, wrap=tk.WORD, width=80, height=30)
        self.report_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
    def setup_visualization_tab(self):
        """Setup the density-temperature grid visualization tab"""
        viz_frame = ttk.Frame(self.notebook)
        self.notebook.add(viz_frame, text="D-T Grid Visualization")
        
        viz_frame.columnconfigure(0, weight=1)
        viz_frame.columnconfigure(1, weight=1)
        viz_frame.rowconfigure(1, weight=1)  # Plot area: expanded
        
        # Controls
        viz_controls = ttk.LabelFrame(viz_frame, text="Visualization Controls", padding="10")
        viz_controls.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(viz_controls, text="EoS Type:").grid(row=0, column=0, padx=(0, 10))
        
        self.eos_type_var = tk.StringVar(value="total")
        self.eos_type_combo = ttk.Combobox(viz_controls, textvariable=self.eos_type_var, 
                                          values=["total", "ele", "ion", "ioncc", "cc"], state="readonly")
        self.eos_type_combo.grid(row=0, column=1, padx=(0, 20))
        
        ttk.Button(viz_controls, text="Generate Plot", command=self.plot_dt_grid).grid(row=0, column=2, padx=(0, 10))
        ttk.Button(viz_controls, text="Save Plot", command=self.save_dt_plot).grid(row=0, column=3)
        
        # Plot area - now spans both columns for larger size
        self.viz_frame_plot = ttk.Frame(viz_frame)
        self.viz_frame_plot.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.viz_frame_plot.columnconfigure(0, weight=1)
        self.viz_frame_plot.rowconfigure(0, weight=1)
        
        self.viz_canvas = None
        self.viz_toolbar = None
        
        # Density data section (left column)
        density_data_frame = ttk.LabelFrame(viz_frame, text="Density Data", padding="5")
        density_data_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0), padx=(0, 5))
        
        # Density data display
        self.density_data_text = tk.Text(density_data_frame, height=8, width=50, wrap=tk.NONE)
        density_scrollbar = ttk.Scrollbar(density_data_frame, orient=tk.VERTICAL, command=self.density_data_text.yview)
        self.density_data_text.configure(yscrollcommand=density_scrollbar.set)
        self.density_data_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        density_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Density options and copy
        density_options_frame = ttk.Frame(density_data_frame)
        density_options_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        
        self.density_type_var = tk.StringVar(value="mass")
        ttk.Radiobutton(density_options_frame, text="Mass Density", variable=self.density_type_var, 
                       value="mass", command=self.update_density_display).grid(row=0, column=0, padx=(0, 10))
        ttk.Radiobutton(density_options_frame, text="Ion Density", variable=self.density_type_var, 
                       value="ion", command=self.update_density_display).grid(row=0, column=1, padx=(0, 10))
        ttk.Button(density_options_frame, text="Copy Data", command=self.copy_density_data).grid(row=0, column=2)
        
        # Temperature data section (right column)
        temp_data_frame = ttk.LabelFrame(viz_frame, text="Temperature Data", padding="5")
        temp_data_frame.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=(10, 0), padx=(5, 0))
        
        # Temperature data display
        self.temp_data_text = tk.Text(temp_data_frame, height=8, width=50, wrap=tk.NONE)
        temp_scrollbar = ttk.Scrollbar(temp_data_frame, orient=tk.VERTICAL, command=self.temp_data_text.yview)
        self.temp_data_text.configure(yscrollcommand=temp_scrollbar.set)
        self.temp_data_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        temp_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Temperature copy button
        temp_options_frame = ttk.Frame(temp_data_frame)
        temp_options_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        ttk.Button(temp_options_frame, text="Copy Data", command=self.copy_temp_data).grid(row=0, column=0)
        
    def setup_internal_energy_tab(self):
        """Setup the internal energy analysis tab"""
        ie_frame = ttk.Frame(self.notebook)
        self.notebook.add(ie_frame, text="Internal Energy Analysis")
        
        ie_frame.columnconfigure(0, weight=1)
        ie_frame.rowconfigure(2, weight=1)
        
        # Controls
        ie_controls = ttk.LabelFrame(ie_frame, text="Internal Energy Analysis", padding="10")
        ie_controls.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(ie_controls, text="EoS Type:").grid(row=0, column=0, padx=(0, 10))
        
        self.ie_eos_type_var = tk.StringVar(value="total")
        self.ie_eos_type_combo = ttk.Combobox(ie_controls, textvariable=self.ie_eos_type_var,
                                             values=["total", "ele", "ion", "ioncc"], state="readonly")
        self.ie_eos_type_combo.grid(row=0, column=1, padx=(0, 20))
        
        ttk.Button(ie_controls, text="Analyze & Plot", command=self.analyze_internal_energy).grid(row=0, column=2, padx=(0, 10))
        ttk.Button(ie_controls, text="Save Plot", command=self.save_ie_plot).grid(row=0, column=3)
        
        # Results display
        results_frame = ttk.LabelFrame(ie_frame, text="Analysis Results", padding="10")
        results_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        results_frame.columnconfigure(1, weight=1)
        
        ttk.Label(results_frame, text="Min Positive Energy Temperature:").grid(row=0, column=0, padx=(0, 10))
        self.min_temp_label = ttk.Label(results_frame, text="Not calculated", foreground="red")
        self.min_temp_label.grid(row=0, column=1, sticky=tk.W)
        
        # Plot area
        self.ie_frame_plot = ttk.Frame(ie_frame)
        self.ie_frame_plot.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.ie_frame_plot.columnconfigure(0, weight=1)
        self.ie_frame_plot.rowconfigure(0, weight=1)
        
        self.ie_canvas = None
        self.ie_toolbar = None
        
    def setup_pressure_tab(self):
        """Setup the pressure analysis tab"""
        pres_frame = ttk.Frame(self.notebook)
        self.notebook.add(pres_frame, text="Pressure Analysis")
        
        pres_frame.columnconfigure(0, weight=1)
        pres_frame.rowconfigure(1, weight=1)
        
        # Controls
        pres_controls = ttk.LabelFrame(pres_frame, text="Pressure Analysis", padding="10")
        pres_controls.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(pres_controls, text="EoS Type:").grid(row=0, column=0, padx=(0, 10))
        
        self.pres_eos_type_var = tk.StringVar(value="total")
        self.pres_eos_type_combo = ttk.Combobox(pres_controls, textvariable=self.pres_eos_type_var,
                                               values=["total", "ele", "ion", "ioncc"], state="readonly")
        self.pres_eos_type_combo.grid(row=0, column=1, padx=(0, 20))
        
        ttk.Button(pres_controls, text="Analyze & Plot", command=self.analyze_pressure).grid(row=0, column=2, padx=(0, 10))
        ttk.Button(pres_controls, text="Save Plot", command=self.save_pres_plot).grid(row=0, column=3)
        
        # Plot area
        self.pres_frame_plot = ttk.Frame(pres_frame)
        self.pres_frame_plot.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.pres_frame_plot.columnconfigure(0, weight=1)
        self.pres_frame_plot.rowconfigure(0, weight=1)
        
        self.pres_canvas = None
        self.pres_toolbar = None
        
    def setup_conversion_tab(self):
        """Setup the SES to CN4 conversion tab"""
        conv_frame = ttk.Frame(self.notebook)
        self.notebook.add(conv_frame, text="SES to CN4 Conversion")
        
        conv_frame.columnconfigure(0, weight=1)
        conv_frame.rowconfigure(3, weight=1)
        
        # Parameters frame
        params_frame = ttk.LabelFrame(conv_frame, text="Conversion Parameters", padding="10")
        params_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Parameter inputs
        self.setup_conversion_parameters(params_frame)
        
        # Conversion status frame
        status_frame = ttk.LabelFrame(conv_frame, text="Conversion Status", padding="10")
        status_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        status_frame.columnconfigure(1, weight=1)
        
        # Check and display converter status
        converter_status = self.converter.get_converter_status()
        
        if converter_status['conversion_possible']:
            if converter_status['hedp_available']:
                status_text = "✅ Full conversion functionality available"
                status_color = "green"
            else:
                status_text = "⚠️  Limited conversion (opacplot2-only mode)"
                status_color = "orange"
        else:
            status_text = "❌ Conversion not available"
            status_color = "red"
        
        ttk.Label(status_frame, text="Status:").grid(row=0, column=0, sticky=tk.W)
        status_label = ttk.Label(status_frame, text=status_text, foreground=status_color)
        status_label.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        if converter_status['limitations']:
            ttk.Label(status_frame, text="Notes:").grid(row=1, column=0, sticky=tk.W)
            notes_text = "; ".join(converter_status['limitations'])
            ttk.Label(status_frame, text=notes_text, foreground="gray").grid(row=1, column=1, sticky=tk.W, padx=(10, 0))
        
        # Conversion controls
        controls_frame = ttk.LabelFrame(conv_frame, text="Conversion Controls", padding="10")
        controls_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(controls_frame, text="Load Suggested Parameters", 
                  command=self.load_suggested_params).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(controls_frame, text="Validate Parameters", 
                  command=self.validate_conversion_params).grid(row=0, column=1, padx=(0, 10))
        ttk.Button(controls_frame, text="Convert to CN4", 
                  command=self.convert_to_cn4).grid(row=0, column=2, padx=(0, 10))
        ttk.Button(controls_frame, text="Select Output Directory", 
                  command=self.select_output_dir).grid(row=0, column=3)
        
        # Output directory display
        self.output_dir_var = tk.StringVar(value=os.getcwd())
        ttk.Label(controls_frame, text="Output Dir:").grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        ttk.Label(controls_frame, textvariable=self.output_dir_var, 
                 foreground="blue").grid(row=1, column=1, columnspan=3, sticky=tk.W, pady=(5, 0))
        
        # Log area
        log_frame = ttk.LabelFrame(conv_frame, text="Conversion Log", padding="5")
        log_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.conv_log = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, height=15)
        self.conv_log.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
    def setup_conversion_parameters(self, parent):
        """Setup conversion parameter input fields"""
        # Create parameter input variables
        self.param_vars = {
            'Znum': tk.StringVar(value='1,6'),
            'Xfracs': tk.StringVar(value='0.5,0.5'),
            'tabnum': tk.StringVar(),
            'Tmin': tk.StringVar(),
            'outname': tk.StringVar(),
            'verbose': tk.BooleanVar(value=True)
        }
        
        # Parameter labels and entries
        param_info = self.converter.get_conversion_options()['parameters']
        
        row = 0
        for param, var in self.param_vars.items():
            if param == 'verbose':
                ttk.Checkbutton(parent, text="Verbose Output", 
                               variable=var).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=2)
            else:
                ttk.Label(parent, text=f"{param}:").grid(row=row, column=0, sticky=tk.W, padx=(0, 10), pady=2)
                
                entry = ttk.Entry(parent, textvariable=var, width=40)
                entry.grid(row=row, column=1, sticky=tk.W, pady=2)
                
                # Add help text
                if param in param_info:
                    help_text = param_info[param].get('description', '')
                    example = param_info[param].get('example', '')
                    tooltip = f"{help_text}"
                    if example:
                        tooltip += f" (e.g., {example})"
                    
                    help_label = ttk.Label(parent, text="(?)", foreground="blue")
                    help_label.grid(row=row, column=2, padx=(5, 0), pady=2)
                    
                    # Bind tooltip (simplified)
                    help_label.bind("<Button-1>", lambda e, msg=tooltip: messagebox.showinfo("Parameter Help", msg))
            
            row += 1
    
    def update_status(self, message):
        """Update status label"""
        self.status_label.config(text=message)
        self.root.update_idletasks()
    
    def update_progress(self, value):
        """Update progress bar"""
        self.progress_var.set(value)
        self.root.update_idletasks()
    
    def load_file(self):
        """Load SESAME file"""
        file_path = filedialog.askopenfilename(
            title="Select SESAME File",
            filetypes=[
                ("SESAME files", "*.ses"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            self.update_status("Loading SESAME file...")
            self.update_progress(20)
            
            success, message = self.analyzer.load_sesame_file(file_path)
            
            if success:
                self.current_file = file_path
                self.file_label.config(text=os.path.basename(file_path))
                self.material_info = self.analyzer.get_material_info()
                self.update_available_types()
                self.update_status(f"Loaded: {message}")
                self.update_progress(100)
                
                # Auto-generate initial report
                self.generate_report()
            else:
                messagebox.showerror("Error", f"Failed to load file:\n{message}")
                self.update_status("Ready - Load a SES file to begin")
                self.update_progress(0)
    
    def reload_file(self):
        """Reload current file"""
        if self.current_file:
            success, message = self.analyzer.load_sesame_file(self.current_file)
            if success:
                self.material_info = self.analyzer.get_material_info()
                self.update_available_types()
                self.update_status(f"Reloaded: {message}")
            else:
                messagebox.showerror("Error", f"Failed to reload file:\n{message}")
    
    def update_available_types(self):
        """Update EoS type comboboxes with available types"""
        if self.material_info:
            available_types = self.material_info.get('available_types', [])
            
            self.eos_type_combo['values'] = available_types
            self.ie_eos_type_combo['values'] = available_types
            self.pres_eos_type_combo['values'] = available_types
            
            if available_types:
                default_type = 'total' if 'total' in available_types else available_types[0]
                self.eos_type_var.set(default_type)
                self.ie_eos_type_var.set(default_type)
                self.pres_eos_type_var.set(default_type)
    
    def generate_report(self):
        """Generate and display material analysis report"""
        if not self.analyzer.data_loaded:
            messagebox.showwarning("Warning", "No data loaded. Please load a SESAME file first.")
            return
        
        self.update_status("Generating report...")
        report = self.analyzer.generate_report()
        
        self.report_text.delete(1.0, tk.END)
        self.report_text.insert(tk.END, report)
        self.update_status("Report generated")
    
    def save_report(self):
        """Save report to file"""
        if not self.report_text.get(1.0, tk.END).strip():
            messagebox.showwarning("Warning", "No report to save.")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Save Report",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            with open(file_path, 'w') as f:
                f.write(self.report_text.get(1.0, tk.END))
            messagebox.showinfo("Success", f"Report saved to {file_path}")
    
    def plot_dt_grid(self):
        """Plot density-temperature grid"""
        if not self.analyzer.data_loaded:
            messagebox.showwarning("Warning", "No data loaded. Please load a SESAME file first.")
            return
        
        self.update_status("Generating D-T grid plot...")
        
        try:
            eos_type = self.eos_type_var.get()
            fig, message = self.analyzer.plot_density_temperature_grid(eos_type)
            
            if fig:
                self.display_plot(fig, self.viz_frame_plot, 'viz')
                self.update_data_displays(eos_type)
                self.update_status(message)
            else:
                messagebox.showerror("Error", f"Failed to generate plot: {message}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Plot generation failed: {str(e)}")
            self.update_status("Ready")
    
    def save_dt_plot(self):
        """Save density-temperature plot"""
        self.save_current_plot('viz', "Save D-T Grid Plot")
    
    def analyze_internal_energy(self):
        """Analyze internal energy distribution"""
        if not self.analyzer.data_loaded:
            messagebox.showwarning("Warning", "No data loaded. Please load a SESAME file first.")
            return
        
        self.update_status("Analyzing internal energy distribution...")
        
        try:
            eos_type = self.ie_eos_type_var.get()
            fig, message, min_temp = self.analyzer.plot_internal_energy_distribution(eos_type)
            
            if fig:
                self.display_plot(fig, self.ie_frame_plot, 'ie')
                
                # Update minimum temperature display
                if min_temp is not None:
                    self.min_temp_label.config(text=f"{min_temp:.2e} eV", foreground="green")
                else:
                    self.min_temp_label.config(text="No positive energy found", foreground="red")
                
                self.update_status(message)
            else:
                messagebox.showerror("Error", f"Failed to analyze: {message}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Analysis failed: {str(e)}")
            self.update_status("Ready")
    
    def save_ie_plot(self):
        """Save internal energy plot"""
        self.save_current_plot('ie', "Save Internal Energy Plot")
    
    def analyze_pressure(self):
        """Analyze pressure distribution"""
        if not self.analyzer.data_loaded:
            messagebox.showwarning("Warning", "No data loaded. Please load a SESAME file first.")
            return
        
        self.update_status("Analyzing pressure distribution...")
        
        try:
            eos_type = self.pres_eos_type_var.get()
            fig, message, _ = self.analyzer.plot_pressure_distribution(eos_type)
            
            if fig:
                self.display_plot(fig, self.pres_frame_plot, 'pres')
                self.update_status(message)
            else:
                messagebox.showerror("Error", f"Failed to analyze: {message}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Analysis failed: {str(e)}")
            self.update_status("Ready")
    
    def save_pres_plot(self):
        """Save pressure plot"""
        self.save_current_plot('pres', "Save Pressure Plot")
    
    def display_plot(self, fig, parent_frame, plot_type):
        """Display matplotlib figure in tkinter frame"""
        # Clear previous plot
        for widget in parent_frame.winfo_children():
            widget.destroy()
        
        # Create a container frame for the plot
        plot_container = ttk.Frame(parent_frame)
        plot_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        plot_container.columnconfigure(0, weight=1)
        plot_container.rowconfigure(0, weight=1)
        
        # Create canvas
        canvas = FigureCanvasTkAgg(fig, plot_container)
        canvas.draw()
        canvas.get_tk_widget().grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create toolbar frame to avoid layout conflicts
        toolbar_frame = ttk.Frame(plot_container)
        toolbar_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Create toolbar with pack inside toolbar_frame
        toolbar = NavigationToolbar2Tk(canvas, toolbar_frame)
        toolbar.update()
        toolbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Store references
        if plot_type == 'viz':
            self.viz_canvas = canvas
            self.viz_toolbar = toolbar
        elif plot_type == 'ie':
            self.ie_canvas = canvas
            self.ie_toolbar = toolbar
        elif plot_type == 'pres':
            self.pres_canvas = canvas
            self.pres_toolbar = toolbar
        
        plt.close(fig)  # Close the figure to free memory
    
    def save_current_plot(self, plot_type, title):
        """Save currently displayed plot"""
        canvas = None
        if plot_type == 'viz':
            canvas = self.viz_canvas
        elif plot_type == 'ie':
            canvas = self.ie_canvas
        elif plot_type == 'pres':
            canvas = self.pres_canvas
        
        if not canvas:
            messagebox.showwarning("Warning", "No plot to save.")
            return
        
        file_path = filedialog.asksaveasfilename(
            title=title,
            defaultextension=".png",
            filetypes=[
                ("PNG files", "*.png"),
                ("PDF files", "*.pdf"),
                ("SVG files", "*.svg"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            canvas.figure.savefig(file_path, dpi=150, bbox_inches='tight')
            messagebox.showinfo("Success", f"Plot saved to {file_path}")
    
    def select_output_dir(self):
        """Select output directory for conversion"""
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.output_dir_var.set(directory)
    
    def load_suggested_params(self):
        """Load suggested conversion parameters"""
        if not self.material_info:
            messagebox.showwarning("Warning", "No material data loaded.")
            return
        
        suggestions = self.converter.get_suggested_parameters(self.material_info)
        
        for param, value in suggestions.items():
            if param in self.param_vars and value:
                self.param_vars[param].set(str(value))
        
        self.update_conversion_log("Loaded suggested parameters")
    
    def validate_conversion_params(self):
        """Validate conversion parameters"""
        params = {param: var.get() for param, var in self.param_vars.items()}
        errors = self.converter.validate_parameters(params)
        
        if errors:
            error_message = "Parameter validation failed:\n" + "\n".join(f"• {error}" for error in errors)
            messagebox.showerror("Validation Error", error_message)
            self.update_conversion_log(f"Validation failed: {len(errors)} errors")
        else:
            messagebox.showinfo("Success", "All parameters are valid!")
            self.update_conversion_log("Parameters validated successfully")
    
    def convert_to_cn4(self):
        """Convert SESAME file to CN4 format"""
        if not self.current_file:
            messagebox.showwarning("Warning", "No SESAME file loaded.")
            return
        
        # Get parameters
        params = {param: var.get() for param, var in self.param_vars.items()}
        
        # Validate parameters
        errors = self.converter.validate_parameters(params)
        if errors:
            error_message = "Parameter validation failed:\n" + "\n".join(f"• {error}" for error in errors)
            messagebox.showerror("Validation Error", error_message)
            return
        
        # Get output directory
        output_dir = self.output_dir_var.get()
        if not os.path.exists(output_dir):
            messagebox.showerror("Error", "Output directory does not exist.")
            return
        
        self.update_conversion_log("Starting conversion...")
        self.update_status("Converting to CN4...")
        
        # Run conversion in thread
        def conversion_thread():
            def progress_callback(message):
                self.root.after(0, lambda: self.update_conversion_log(message))
            
            success, output_file, message = self.converter.convert_file(
                self.current_file, output_dir, params, progress_callback
            )
            
            # Update GUI from main thread
            self.root.after(0, lambda: self.conversion_complete(success, output_file, message))
        
        thread = threading.Thread(target=conversion_thread)
        thread.daemon = True
        thread.start()
    
    def conversion_complete(self, success, output_file, message):
        """Handle conversion completion"""
        self.update_conversion_log(message)
        
        if success:
            self.update_status("Conversion completed successfully")
            messagebox.showinfo("Success", f"Conversion completed!\n\n{message}")
        else:
            self.update_status("Conversion failed")
            messagebox.showerror("Conversion Failed", message)
    
    def update_conversion_log(self, message):
        """Update conversion log"""
        self.conv_log.insert(tk.END, f"{message}\n")
        self.conv_log.see(tk.END)
        self.root.update_idletasks()
    
    def update_data_displays(self, eos_type):
        """Update density and temperature data displays"""
        if not self.analyzer.data_loaded:
            return
        
        try:
            # Get data from analyzer
            eos_data = self.analyzer.eos_data
            dens_key = f"{eos_type}_dens"
            temp_key = f"{eos_type}_temps"
            
            if dens_key not in eos_data or temp_key not in eos_data:
                return
            
            self.current_densities = eos_data[dens_key]
            self.current_temperatures = eos_data[temp_key]
            self.current_ion_densities = self.analyzer._calculate_ion_densities(self.current_densities)
            
            # Update density display
            self.update_density_display()
            
            # Update temperature display
            self.update_temperature_display()
            
        except Exception as e:
            print(f"Error updating data displays: {e}")
    
    def update_density_display(self):
        """Update density data display based on selected type"""
        if not hasattr(self, 'current_densities'):
            return
        
        self.density_data_text.delete(1.0, tk.END)
        
        density_type = self.density_type_var.get()
        if density_type == "mass":
            densities = self.current_densities
            header = "Index\tMass Density (g/cm³)\n"
        else:  # ion
            densities = self.current_ion_densities
            header = "Index\tIon Density (atoms/cm³)\n"
        
        self.density_data_text.insert(tk.END, header)
        
        for i, dens in enumerate(densities):
            if dens > 1e-10:  # Only show valid data
                self.density_data_text.insert(tk.END, f"{i}\t{dens:.6e}\n")
    
    def update_temperature_display(self):
        """Update temperature data display"""
        if not hasattr(self, 'current_temperatures'):
            return
        
        self.temp_data_text.delete(1.0, tk.END)
        self.temp_data_text.insert(tk.END, "Index\tTemperature (eV)\n")
        
        for i, temp in enumerate(self.current_temperatures):
            if temp > 1e-10:  # Only show valid data
                self.temp_data_text.insert(tk.END, f"{i}\t{temp:.6e}\n")
    
    def copy_density_data(self):
        """Copy density data to clipboard"""
        try:
            data = self.density_data_text.get(1.0, tk.END)
            if data.strip():
                self.root.clipboard_clear()
                self.root.clipboard_append(data)
                density_type = "Mass" if self.density_type_var.get() == "mass" else "Ion"
                messagebox.showinfo("Success", f"{density_type} density data copied to clipboard")
            else:
                messagebox.showinfo("Info", "No density data to copy.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy density data: {str(e)}")
    
    def copy_temp_data(self):
        """Copy temperature data to clipboard"""
        try:
            data = self.temp_data_text.get(1.0, tk.END)
            if data.strip():
                self.root.clipboard_clear()
                self.root.clipboard_append(data)
                messagebox.showinfo("Success", "Temperature data copied to clipboard")
            else:
                messagebox.showinfo("Info", "No temperature data to copy.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy temperature data: {str(e)}")

    def show_about(self):
        """Show about dialog"""
        about_text = """SESAME EoS Analysis Tool v2.2.0

A standalone GUI application for analyzing SESAME equation of state files.

Features:
• Load and analyze SESAME EoS files
• Generate comprehensive material reports  
• Visualize density-temperature grids with data tables
• Analyze pressure distributions with positive pressure detection
• Analyze internal energy with improved positive energy algorithm
• Enhanced interactive plots showing data values on hover
• Convert SESAME files to CN4/IONMIX format

Built with Python, tkinter, matplotlib, and opacplot2

New in v2.2.0:
• Grid data tables for easy copy/paste operations
• Enhanced D-T Grid visualization with detailed data display
• Ion density coordinate axis support
• Improved material reports with ion density information

Dependencies automatically managed - runs out of the box!
"""
        messagebox.showinfo("About", about_text)

def main():
    """Main application entry point"""
    root = tk.Tk()
    app = SESAMEAnalysisGUI(root)
    
    # Set window icon (if available)
    try:
        # You can add an icon file here if available
        # root.iconbitmap("icon.ico")
        pass
    except:
        pass
    
    root.mainloop()

if __name__ == "__main__":
    main()
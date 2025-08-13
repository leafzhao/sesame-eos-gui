"""
SESAME Data Analyzer Module
Based on opacplot2_SESAME_EoS_Analysis_7592_Final.ipynb

This module provides functionality to read, analyze and visualize SESAME EoS data.
"""

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm, SymLogNorm
import os
import warnings
warnings.filterwarnings('ignore')

# Import opacplot2 with error handling
try:
    import opacplot2 as opp
except ImportError as e:
    print(f"Warning: opacplot2 not found. Please run 'python setup.py' first.")
    print(f"Error: {e}")
    raise ImportError("opacplot2 is required but not installed. Run setup.py to install dependencies.")

# Disable LaTeX rendering to avoid dependency issues
plt.rcParams['text.usetex'] = False
matplotlib.rcParams['text.usetex'] = False
plt.rcParams['mathtext.default'] = 'regular'
plt.rcParams['font.family'] = 'DejaVu Sans'

# Set matplotlib to use TkAgg backend for GUI compatibility
try:
    matplotlib.use('TkAgg')
except ImportError:
    # Fallback to default backend if TkAgg is not available
    pass

class SESAMEAnalyzer:
    """Class to handle SESAME file analysis and visualization"""
    
    def __init__(self):
        self.sesame_data = None
        self.eos_data = None
        self.material_id = None
        self.available_eos_types = []
        self.data_loaded = False
        
    def load_sesame_file(self, file_path):
        """Load SESAME file and return basic information"""
        try:
            if not os.path.exists(file_path):
                return False, f"File not found: {file_path}"
            
            # Try double precision first
            try:
                self.sesame_data = opp.OpgSesame(file_path, opp.OpgSesame.DOUBLE, verbose=False)
            except:
                self.sesame_data = opp.OpgSesame(file_path, opp.OpgSesame.SINGLE, verbose=False)
            
            # Get material IDs
            material_ids = list(self.sesame_data.data.keys())
            if not material_ids:
                return False, "No material data found in file"
            
            # Use first material ID
            self.material_id = material_ids[0]
            self.eos_data = self.sesame_data.data[self.material_id]
            
            # Analyze available EoS types
            self._analyze_eos_types()
            
            self.data_loaded = True
            return True, f"Successfully loaded material ID {self.material_id}"
            
        except Exception as e:
            return False, f"Error loading file: {str(e)}"
    
    def _analyze_eos_types(self):
        """Analyze available EoS data types"""
        self.available_eos_types = []
        for eos_type in ['total', 'ele', 'ion', 'ioncc', 'cc']:
            dens_key = f"{eos_type}_dens"
            temp_key = f"{eos_type}_temps"
            if dens_key in self.eos_data and temp_key in self.eos_data:
                densities = self.eos_data[dens_key]
                temperatures = self.eos_data[temp_key]
                valid_dens = np.sum(densities > 1e-10)
                valid_temp = np.sum(temperatures > 1e-10)
                if valid_dens > 5 and valid_temp > 5:
                    self.available_eos_types.append(eos_type)
    
    def get_material_info(self):
        """Get basic material information"""
        if not self.data_loaded:
            return {}
        
        info = {
            'material_id': self.material_id,
            'abar': self.eos_data.get('abar', 'N/A'),
            'zmax': self.eos_data.get('zmax', 'N/A'), 
            'rho0': self.eos_data.get('rho0', 'N/A'),
            'bulkmod': self.eos_data.get('bulkmod', 'N/A'),
            'available_types': self.available_eos_types
        }
        return info
    
    def generate_report(self):
        """Generate comprehensive analysis report"""
        if not self.data_loaded:
            return "No data loaded"
        
        report = []
        report.append("=" * 60)
        report.append(f"SESAME EoS Data Analysis Report")
        report.append("=" * 60)
        
        # Material properties
        report.append(f"\nMaterial Properties:")
        report.append(f"  Material ID: {self.material_id}")
        
        abar = self.eos_data.get('abar', 'N/A')
        if abar != 'N/A':
            report.append(f"  Average atomic mass: {abar:.3f} amu")
        else:
            report.append(f"  Average atomic mass: N/A")
        
        zmax = self.eos_data.get('zmax', 'N/A')
        if zmax != 'N/A':
            report.append(f"  Average atomic number: {zmax:.1f}")
        else:
            report.append(f"  Average atomic number: N/A")
        
        rho0 = self.eos_data.get('rho0', 'N/A')
        if rho0 != 'N/A':
            report.append(f"  Standard density: {rho0:.3f} g/cm³")
        else:
            report.append(f"  Standard density: N/A")
        
        # Data coverage
        report.append(f"\nData Coverage:")
        total_points = 0
        for eos_type in self.available_eos_types:
            dens_key = f"{eos_type}_dens"
            temp_key = f"{eos_type}_temps"
            
            if dens_key in self.eos_data and temp_key in self.eos_data:
                densities = self.eos_data[dens_key]
                temperatures = self.eos_data[temp_key]
                
                valid_dens = np.sum(densities > 1e-10)
                valid_temp = np.sum(temperatures > 1e-10)
                points = valid_dens * valid_temp
                total_points += points
                
                nonzero_dens = densities[densities > 1e-10]
                nonzero_temp = temperatures[temperatures > 1e-10]
                
                report.append(f"  {eos_type.upper()} EoS:")
                report.append(f"    Grid: {valid_dens} x {valid_temp} points")
                if len(nonzero_dens) > 0:
                    report.append(f"    Density range: {nonzero_dens.min():.2e} - {nonzero_dens.max():.2e} g/cm³")
                if len(nonzero_temp) > 0:
                    report.append(f"    Temperature range: {nonzero_temp.min():.2e} - {nonzero_temp.max():.2e} eV")
        
        report.append(f"\nTotal effective data points: {total_points:,}")
        
        # Data quality assessment
        report.append(f"\nData Quality Assessment:")
        for eos_type in self.available_eos_types:
            pres_key = f"{eos_type}_pres"
            eint_key = f"{eos_type}_eint"
            
            if pres_key in self.eos_data:
                pressure_data = self.eos_data[pres_key]
                total_p = pressure_data.size
                negative_p = np.sum(pressure_data < 0)
                zero_p = np.sum(pressure_data == 0)
                report.append(f"  {eos_type.upper()} pressure: {negative_p}/{total_p} negative ({negative_p/total_p*100:.1f}%)")
            
            if eint_key in self.eos_data:
                eint_data = self.eos_data[eint_key]
                total_e = eint_data.size
                negative_e = np.sum(eint_data < 0)
                report.append(f"  {eos_type.upper()} internal energy: {negative_e}/{total_e} negative ({negative_e/total_e*100:.1f}%)")
        
        return "\n".join(report)
    
    def plot_density_temperature_grid(self, eos_type='total', save_path=None):
        """Plot density-temperature grid visualization"""
        if not self.data_loaded:
            return None, "No data loaded"
        
        if eos_type not in self.available_eos_types:
            eos_type = self.available_eos_types[0] if self.available_eos_types else 'total'
        
        dens_key = f"{eos_type}_dens"
        temp_key = f"{eos_type}_temps"
        
        if dens_key not in self.eos_data or temp_key not in self.eos_data:
            return None, f"No {eos_type} density/temperature data found"
        
        densities = self.eos_data[dens_key]
        temperatures = self.eos_data[temp_key]
        
        # Filter valid data
        nonzero_dens = densities[densities > 1e-10]
        nonzero_temp = temperatures[temperatures > 1e-10]
        
        # Create plot
        with plt.rc_context({'text.usetex': False, 'mathtext.default': 'regular'}):
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7))
            fig.subplots_adjust(left=0.08, right=0.95, top=0.92, bottom=0.12, wspace=0.25)
            
            if len(nonzero_dens) > 0:
                dens_indices = np.where(densities > 1e-10)[0]
                ax1.plot(dens_indices, nonzero_dens, 'bo-', markersize=4, alpha=0.7)
                ax1.set_xlabel('Grid Point Index')
                ax1.set_ylabel('Density [g/cm³]')
                ax1.set_yscale('log')
                ax1.set_title(f'{eos_type.upper()} EoS Density Grid\n({len(nonzero_dens)}/{len(densities)} valid points)')
                ax1.grid(True, alpha=0.3)
            
            if len(nonzero_temp) > 0:
                temp_indices = np.where(temperatures > 1e-10)[0]
                ax2.plot(temp_indices, nonzero_temp, 'ro-', markersize=4, alpha=0.7)
                ax2.set_xlabel('Grid Point Index')
                ax2.set_ylabel('Temperature [eV]')
                ax2.set_yscale('log')
                ax2.set_title(f'{eos_type.upper()} EoS Temperature Grid\n({len(nonzero_temp)}/{len(temperatures)} valid points)')
                ax2.grid(True, alpha=0.3)
            
            # Layout is already adjusted above, no need for tight_layout
            
            if save_path:
                fig.savefig(save_path, dpi=150, bbox_inches='tight')
            
            return fig, "Grid visualization completed"
    
    def plot_internal_energy_distribution(self, eos_type='total', save_path=None):
        """Plot internal energy distribution and find minimum positive energy temperature"""
        if not self.data_loaded:
            return None, "No data loaded", None
        
        if eos_type not in self.available_eos_types:
            eos_type = self.available_eos_types[0] if self.available_eos_types else 'total'
        
        dens_key = f"{eos_type}_dens"
        temp_key = f"{eos_type}_temps"
        eint_key = f"{eos_type}_eint"
        
        if any(key not in self.eos_data for key in [dens_key, temp_key, eint_key]):
            return None, f"Incomplete {eos_type} internal energy data", None
        
        densities = self.eos_data[dens_key]
        temperatures = self.eos_data[temp_key]
        internal_energy = self.eos_data[eint_key]
        
        # Filter valid data
        valid_dens_mask = densities > 1e-10
        valid_temp_mask = temperatures > 1e-10
        
        valid_densities = densities[valid_dens_mask]
        valid_temperatures = temperatures[valid_temp_mask]
        valid_internal_energy = internal_energy[np.ix_(valid_dens_mask, valid_temp_mask)]
        
        # Find minimum temperature where ALL densities have positive internal energy
        # Algorithm: For each density, find the minimum temperature index where energy > 0
        # Then take the maximum of these indices to ensure ALL densities are positive
        min_positive_temp = None
        min_temp_indices = []
        
        for density_idx in range(len(valid_densities)):
            # Find first temperature index where energy > 0 for this density
            positive_mask = valid_internal_energy[density_idx, :] > 0
            if np.any(positive_mask):
                first_positive_idx = np.where(positive_mask)[0][0]
                min_temp_indices.append(first_positive_idx)
            else:
                # If no positive energy for this density, use last temperature
                min_temp_indices.append(len(valid_temperatures) - 1)
        
        if min_temp_indices:
            # Take the maximum index to ensure ALL densities have positive energy
            max_min_idx = max(min_temp_indices)
            if max_min_idx < len(valid_temperatures):
                min_positive_temp = valid_temperatures[max_min_idx]
        
        # Create plot
        with plt.rc_context({'text.usetex': False, 'mathtext.default': 'regular'}):
            D, T = np.meshgrid(valid_densities, valid_temperatures, indexing='ij')
            fig, ax = plt.subplots(figsize=(12, 9))
            fig.subplots_adjust(left=0.10, right=0.88, top=0.92, bottom=0.12)
            
            # Convert to MJ/kg
            U_MJ = valid_internal_energy / 1e10
            
            if U_MJ.min() < 0:
                abs_max = max(abs(U_MJ.min()), abs(U_MJ.max()))
                norm = SymLogNorm(linthresh=abs_max/1000, vmin=-abs_max, vmax=abs_max)
                cs = ax.contourf(D, T, U_MJ, levels=50, norm=norm, cmap='RdYlBu_r')
            else:
                U_positive = np.where(U_MJ > 1e-6, U_MJ, 1e-6)
                try:
                    if U_positive.max() / U_positive.min() > 100:
                        levels = np.logspace(np.log10(U_positive.min()), 
                                           np.log10(U_positive.max()), 25)
                        cs = ax.contourf(D, T, U_positive, levels=levels, norm=LogNorm(), cmap='plasma')
                    else:
                        cs = ax.contourf(D, T, U_MJ, levels=50, cmap='plasma')
                except ValueError:
                    cs = ax.contourf(D, T, U_MJ, levels=50, cmap='plasma')
            
            cb = plt.colorbar(cs, ax=ax)
            cb.set_label('Internal Energy [MJ/kg]', fontsize=14)
            
            # Enhanced cursor data display
            def format_coord(x, y):
                # Find closest grid points
                try:
                    # Convert back from log scale if needed
                    x_idx = np.argmin(np.abs(valid_densities - x))
                    y_idx = np.argmin(np.abs(valid_temperatures - y))
                    
                    if x_idx < len(valid_densities) and y_idx < len(valid_temperatures):
                        data_value = U_MJ[x_idx, y_idx]
                        return f'ρ={x:.2e} g/cm³, T={y:.2e} eV, U={data_value:.3f} MJ/kg'
                    else:
                        return f'ρ={x:.2e} g/cm³, T={y:.2e} eV'
                except:
                    return f'ρ={x:.2e} g/cm³, T={y:.2e} eV'
            
            ax.format_coord = format_coord
            
            ax.set_xlabel('Density [g/cm³]', fontsize=14)
            ax.set_ylabel('Temperature [eV]', fontsize=14)
            ax.set_title(f'{eos_type.upper()} EoS Internal Energy Distribution', fontsize=16)
            ax.set_xscale('log')
            ax.set_yscale('log')
            
            # Mark minimum positive temperature if found
            if min_positive_temp is not None:
                ax.axhline(min_positive_temp, color='yellow', linestyle='--', linewidth=2, alpha=0.8)
                
                # Position label dynamically based on plot area
                x_pos = valid_densities.min() * (valid_densities.max() / valid_densities.min()) ** 0.2
                y_pos = min_positive_temp * (valid_temperatures.max() / min_positive_temp) ** 0.1
                
                ax.text(x_pos, y_pos, 
                       f'Min positive T = {min_positive_temp:.2e} eV', 
                       bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7, edgecolor='black'),
                       fontsize=10, fontweight='bold')
            
            # Layout is already adjusted above, no need for tight_layout
            
            if save_path:
                fig.savefig(save_path, dpi=150, bbox_inches='tight')
            
            return fig, "Internal energy analysis completed", min_positive_temp
    
    def plot_pressure_distribution(self, eos_type='total', save_path=None):
        """Plot pressure distribution (electron, ion, total)"""
        if not self.data_loaded:
            return None, "No data loaded", None
        
        if eos_type not in self.available_eos_types:
            eos_type = self.available_eos_types[0] if self.available_eos_types else 'total'
        
        dens_key = f"{eos_type}_dens"
        temp_key = f"{eos_type}_temps"
        pres_key = f"{eos_type}_pres"
        
        if any(key not in self.eos_data for key in [dens_key, temp_key, pres_key]):
            return None, f"Incomplete {eos_type} pressure data", None
        
        densities = self.eos_data[dens_key]
        temperatures = self.eos_data[temp_key]
        pressure = self.eos_data[pres_key]
        
        # Filter valid data
        valid_dens_mask = densities > 1e-10
        valid_temp_mask = temperatures > 1e-10
        
        valid_densities = densities[valid_dens_mask]
        valid_temperatures = temperatures[valid_temp_mask]
        valid_pressure = pressure[np.ix_(valid_dens_mask, valid_temp_mask)]
        
        # Find minimum temperature where ALL densities have positive pressure
        # Algorithm: For each density, find the minimum temperature index where pressure > 0
        # Then take the maximum of these indices to ensure ALL densities are positive
        min_positive_pres_temp = None
        min_temp_indices = []
        
        for density_idx in range(len(valid_densities)):
            # Find first temperature index where pressure > 0 for this density
            positive_mask = valid_pressure[density_idx, :] > 0
            if np.any(positive_mask):
                first_positive_idx = np.where(positive_mask)[0][0]
                min_temp_indices.append(first_positive_idx)
            else:
                # If no positive pressure for this density, use last temperature
                min_temp_indices.append(len(valid_temperatures) - 1)
        
        if min_temp_indices:
            # Take the maximum index to ensure ALL densities have positive pressure
            max_min_idx = max(min_temp_indices)
            if max_min_idx < len(valid_temperatures):
                min_positive_pres_temp = valid_temperatures[max_min_idx]
        
        # Create plot
        with plt.rc_context({'text.usetex': False, 'mathtext.default': 'regular'}):
            D, T = np.meshgrid(valid_densities, valid_temperatures, indexing='ij')
            fig, ax = plt.subplots(figsize=(12, 9))
            fig.subplots_adjust(left=0.10, right=0.88, top=0.92, bottom=0.12)
            
            # Convert to GPa (1 dyne/cm² = 1e-10 GPa)
            P_GPa = valid_pressure * 1e-10
            
            if P_GPa.min() < 0:
                abs_max = max(abs(P_GPa.min()), abs(P_GPa.max()))
                norm = SymLogNorm(linthresh=abs_max/1000, vmin=-abs_max, vmax=abs_max)
                cs = ax.contourf(D, T, P_GPa, levels=50, norm=norm, cmap='RdYlBu_r')
            else:
                P_positive = np.where(P_GPa > 1e-6, P_GPa, 1e-6)
                try:
                    if P_positive.max() / P_positive.min() > 100:
                        levels = np.logspace(np.log10(P_positive.min()), 
                                           np.log10(P_positive.max()), 25)
                        cs = ax.contourf(D, T, P_positive, levels=levels, norm=LogNorm(), cmap='viridis')
                    else:
                        cs = ax.contourf(D, T, P_GPa, levels=50, cmap='viridis')
                except ValueError:
                    cs = ax.contourf(D, T, P_GPa, levels=50, cmap='viridis')
            
            cb = plt.colorbar(cs, ax=ax)
            cb.set_label('Pressure [GPa]', fontsize=14)
            
            # Enhanced cursor data display
            def format_coord(x, y):
                # Find closest grid points
                try:
                    # Convert back from log scale if needed
                    x_idx = np.argmin(np.abs(valid_densities - x))
                    y_idx = np.argmin(np.abs(valid_temperatures - y))
                    
                    if x_idx < len(valid_densities) and y_idx < len(valid_temperatures):
                        data_value = P_GPa[x_idx, y_idx]
                        return f'ρ={x:.2e} g/cm³, T={y:.2e} eV, P={data_value:.3f} GPa'
                    else:
                        return f'ρ={x:.2e} g/cm³, T={y:.2e} eV'
                except:
                    return f'ρ={x:.2e} g/cm³, T={y:.2e} eV'
            
            ax.format_coord = format_coord
            
            ax.set_xlabel('Density [g/cm³]', fontsize=14)
            ax.set_ylabel('Temperature [eV]', fontsize=14)
            ax.set_title(f'{eos_type.upper()} EoS Pressure Distribution', fontsize=16)
            ax.set_xscale('log')
            ax.set_yscale('log')
            
            # Mark minimum positive pressure temperature if found
            if min_positive_pres_temp is not None:
                ax.axhline(min_positive_pres_temp, color='cyan', linestyle='--', linewidth=2, alpha=0.8)
                
                # Position label dynamically based on plot area
                x_pos = valid_densities.min() * (valid_densities.max() / valid_densities.min()) ** 0.2
                y_pos = min_positive_pres_temp * (valid_temperatures.max() / min_positive_pres_temp) ** 0.1
                
                ax.text(x_pos, y_pos, 
                       f'Min positive P temp = {min_positive_pres_temp:.2e} eV', 
                       bbox=dict(boxstyle='round', facecolor='cyan', alpha=0.7, edgecolor='black'),
                       fontsize=10, fontweight='bold')
            
            # Layout is already adjusted above, no need for tight_layout
            
            if save_path:
                fig.savefig(save_path, dpi=150, bbox_inches='tight')
            
            return fig, "Pressure analysis completed", min_positive_pres_temp
    
    def get_conversion_parameters(self):
        """Get available parameters for opac_convert"""
        if not self.data_loaded:
            return {}
        
        # Get basic material composition info
        params = {
            'material_id': self.material_id,
            'zmax': self.eos_data.get('zmax', 3.5),
            'abar': self.eos_data.get('abar', 6.51),
            'available_formats': ['ionmix'],
            'suggested_znum': [1, 6],  # H, C for polystyrene-like materials
            'suggested_xfracs': [0.5, 0.5],
            'min_temperature': None,
            'max_temperature': None
        }
        
        # Get temperature range from available data
        if self.available_eos_types:
            eos_type = self.available_eos_types[0]
            temp_key = f"{eos_type}_temps"
            if temp_key in self.eos_data:
                temps = self.eos_data[temp_key]
                valid_temps = temps[temps > 1e-10]
                if len(valid_temps) > 0:
                    params['min_temperature'] = valid_temps.min()
                    params['max_temperature'] = valid_temps.max()
        
        return params
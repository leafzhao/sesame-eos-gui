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
        for eos_type in ['ioncc', 'ele', 'ion', 'total', 'cc']:
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
                
                # Calculate ion densities
                ion_densities = self._calculate_ion_densities(densities)
                nonzero_ion_dens = ion_densities[densities > 1e-10]
                
                report.append(f"  {eos_type.upper()} EoS:")
                report.append(f"    Grid: {valid_dens} x {valid_temp} points")
                if len(nonzero_dens) > 0:
                    report.append(f"    Mass density range: {nonzero_dens.min():.2e} - {nonzero_dens.max():.2e} g/cm³")
                if len(nonzero_ion_dens) > 0:
                    report.append(f"    Ion density range: {nonzero_ion_dens.min():.2e} - {nonzero_ion_dens.max():.2e} atoms/cm³")
                if len(nonzero_temp) > 0:
                    report.append(f"    Temperature range: {nonzero_temp.min():.2e} - {nonzero_temp.max():.2e} eV")
        
        report.append(f"\nTotal effective data points: {total_points:,}")
        
        # Ion density analysis section
        report.append(f"\nIon Density Analysis:")
        abar = self.eos_data.get('abar', 'N/A')
        if abar != 'N/A' and abar > 0:
            report.append(f"  Average atomic mass (abar): {abar:.3f} amu")
            report.append(f"  Ion density calculation: ρ_ion = ρ_mass / (abar × 1.66054×10⁻²⁴)")
            
            # Find the main EoS type for detailed analysis
            main_eos = 'total' if 'total' in self.available_eos_types else self.available_eos_types[0]
            dens_key = f"{main_eos}_dens"
            if dens_key in self.eos_data:
                densities = self.eos_data[dens_key]
                ion_densities = self._calculate_ion_densities(densities)
                nonzero_dens = densities[densities > 1e-10]
                nonzero_ion_dens = ion_densities[densities > 1e-10]
                
                if len(nonzero_dens) > 0 and len(nonzero_ion_dens) > 0:
                    ratio_range = nonzero_ion_dens / nonzero_dens
                    report.append(f"  Ion-to-mass density ratio range: {ratio_range.min():.2e} - {ratio_range.max():.2e}")
        else:
            report.append(f"  Average atomic mass: Not available")
            report.append(f"  Ion density calculation: Using default abar = 10.0 amu")
        
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
        """Plot density-temperature grid visualization with ion density axis"""
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
        
        # Calculate ion densities using the method from opac_converter.py
        ion_densities = self._calculate_ion_densities(densities)
        nonzero_ion_dens = ion_densities[densities > 1e-10]
        
        # Create plot with larger size - ensure clean state and proper spacing
        plt.close('all')  # Close any existing plots
        with plt.rc_context({'text.usetex': False, 'mathtext.default': 'regular'}):
            from matplotlib.gridspec import GridSpec
            
            fig = plt.figure(figsize=(20, 8))
            
            # Use GridSpec for precise control of subplot positions
            gs = GridSpec(1, 2, figure=fig, left=0.05, right=0.95, top=0.92, bottom=0.10, 
                         wspace=0.4, hspace=0.1)
            
            # Create subplots with explicit positioning
            ax1 = fig.add_subplot(gs[0, 0])  # Left subplot for density
            ax2 = fig.add_subplot(gs[0, 1])  # Right subplot for temperature
            
            if len(nonzero_dens) > 0:
                dens_indices = np.where(densities > 1e-10)[0]
                ax1.plot(dens_indices, nonzero_dens, 'bo-', markersize=4, alpha=0.8)
                ax1.set_xlabel('Grid Point Index')
                ax1.set_ylabel('Mass Density [g/cm³]', color='black')
                ax1.set_yscale('log')
                ax1.set_title(f'{eos_type.upper()} EoS Density Grid\n({len(nonzero_dens)}/{len(densities)} valid points)')
                ax1.grid(True, alpha=0.3)
                ax1.tick_params(axis='y', labelcolor='black')
                
                # Add ion density axis on the right - with strict boundary control
                ax1_ion = ax1.twinx()
                if len(nonzero_ion_dens) > 0:
                    ax1_ion.plot(dens_indices, nonzero_ion_dens, 'bo-', markersize=4, alpha=0.8)
                    ax1_ion.set_ylabel('Ion Number Density [atoms/cm³]', color='black', rotation=270, labelpad=15)
                    ax1_ion.set_yscale('log')
                    ax1_ion.tick_params(axis='y', labelcolor='black', labelsize=8)
                    
                    # Strictly confine the ion axis to the left subplot area
                    ax1_ion.spines['right'].set_position(('axes', 1.0))
                    ax1_ion.spines['right'].set_visible(True)
                
                # Remove the density data label as requested
            
            if len(nonzero_temp) > 0:
                temp_indices = np.where(temperatures > 1e-10)[0]
                ax2.plot(temp_indices, nonzero_temp, 'ro-', markersize=4, alpha=0.7)
                ax2.set_xlabel('Grid Point Index')
                ax2.set_ylabel('Temperature [eV]')
                ax2.set_yscale('log')
                ax2.set_title(f'{eos_type.upper()} EoS Temperature Grid\n({len(nonzero_temp)}/{len(temperatures)} valid points)')
                ax2.grid(True, alpha=0.3)
            
            if save_path:
                fig.savefig(save_path, dpi=150, bbox_inches='tight')
            
            return fig, "Grid visualization with ion density completed"
    
    def _calculate_ion_densities(self, mass_densities):
        """Calculate ion number densities from mass densities using opac_converter approach"""
        try:
            # Use similar approach as opac_converter.py
            # This is a simplified calculation - in practice, this would use material properties
            # For now, assume average atomic mass ~ 10 amu for demonstration
            abar = self.eos_data.get('abar', 10.0)  # Average atomic mass
            if abar == 'N/A' or abar <= 0:
                abar = 10.0  # Fallback value
            
            # Convert g/cm³ to atoms/cm³
            # ion_density = mass_density / (abar * atomic_mass_unit)
            # atomic_mass_unit = 1.66054e-24 g
            atomic_mass_unit = 1.66054e-24
            ion_densities = mass_densities / (abar * atomic_mass_unit)
            
            return ion_densities
            
        except Exception as e:
            print(f"Warning: Ion density calculation failed: {e}")
            # Return zeros if calculation fails
            return np.zeros_like(mass_densities)
    
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
            
            # 单位：GPa (原始数据已经是GPa，不需要转换)
            P_GPa = valid_pressure
            
            # --- 优化策略：先填充灰色背景，再覆盖正值区域 ---
            # 第一步：填充整个图表为灰色背景
            ax.contourf(D, T, np.ones_like(P_GPa), levels=[0, 2], colors=['lightgray'], alpha=1.0)
            
            # 第二步：只在正值区域绘制彩色等高线
            tiny = 1e-20
            pos_mask = P_GPa > 0.0
            
            if np.any(pos_mask):
                # 只处理正值数据，避免掩码边界问题
                P_positive = np.where(pos_mask, np.maximum(P_GPa, tiny), tiny)
                
                # 计算对数等级
                pos_values = P_GPa[pos_mask]
                vmin = max(pos_values.min(), tiny)
                vmax = pos_values.max()
                levels = np.logspace(np.log10(vmin), np.log10(vmax), 80)
                
                # 只在正值区域绘制，使用extend='max'避免边界问题
                cs = ax.contourf(D, T, P_positive, levels=levels,
                                norm=LogNorm(vmin=vmin, vmax=vmax),
                                cmap='nipy_spectral', extend='max', antialiased=False)
            else:
                # 如果没有正值，则创建一个虚拟的colorbar
                cs = ax.contourf(D, T, np.ones_like(P_GPa) * tiny, levels=[tiny, tiny*10],
                                norm=LogNorm(vmin=tiny, vmax=tiny*10), cmap='nipy_spectral')
                
            # --- 第三步：添加 P = 0 等值线 ---
            try:
                zero_contour = ax.contour(D, T, P_GPa, levels=[0.0], colors=['k'], 
                                        linewidths=1.5, linestyles='--', alpha=0.8)
                # ax.clabel(zero_contour, inline=True, fontsize=8, fmt='P = 0')
            except:
                pass  # 如果无法绘制P=0等值线，则跳过
            
            # colorbar：美观的10^x指数格式显示
            cb = plt.colorbar(cs, ax=ax)
            cb.set_label('Pressure [GPa] (log scale; gray = P ≤ 0)', fontsize=14)
            
            # 设置colorbar为真正的10^x指数格式并增加显示数值数量
            from matplotlib.ticker import LogFormatterMathtext, LogLocator
            
            # 设置更多的tick位置
            cb.locator = LogLocator(base=10, numticks=12)
            cb.formatter = LogFormatterMathtext(10, labelOnlyBase=False)
            cb.update_ticks()
            
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
                ax.axhline(min_positive_pres_temp, color='w', linestyle='--', linewidth=2, alpha=0.8)
                
                # Position label dynamically based on plot area
                x_pos = valid_densities.min() * (valid_densities.max() / valid_densities.min()) ** 0.2
                y_pos = min_positive_pres_temp * (valid_temperatures.max() / min_positive_pres_temp) ** 0.1
                
                ax.text(x_pos, y_pos, 
                       f'Min positive P temp = {min_positive_pres_temp:.2e} eV', 
                       bbox=dict(boxstyle='round', facecolor='w', alpha=0.7, edgecolor='black'),
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
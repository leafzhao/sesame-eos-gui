"""
OPAC Converter Module
Integrated opac_convert.py functionality for GUI

This module provides GUI-friendly interface for converting SESAME files to other formats.
"""

import os
import tempfile
import subprocess
import sys

# Import opacplot2 with error handling
try:
    import opacplot2 as opp
    OPACPLOT2_AVAILABLE = True
except ImportError as e:
    print(f"Warning: opacplot2 not found. Please run 'python setup.py' first.")
    print(f"Error: {e}")
    OPACPLOT2_AVAILABLE = False
    # Create dummy opacplot2 class for fallback
    class DummyOpacplot2:
        pass
    opp = DummyOpacplot2()

# Check hedp availability
try:
    import hedp
    HEDP_AVAILABLE = True
    HEDP_ERROR = None
except ImportError as e:
    HEDP_AVAILABLE = False
    HEDP_ERROR = f"Import error: {e}"
except Exception as e:
    HEDP_AVAILABLE = False
    HEDP_ERROR = f"Compatibility error: {e}"

class OPACConverter:
    """Class to handle SESAME to other format conversions"""
    
    def __init__(self):
        self.available_input_formats = ['sesame', 'propaceos', 'multi', 'sesame-qeos', 'tops']
        self.available_output_formats = ['ionmix']
        self.opacplot2_available = OPACPLOT2_AVAILABLE
        self.hedp_available = HEDP_AVAILABLE
        self.hedp_error = HEDP_ERROR
        
    def get_conversion_options(self):
        """Get available conversion parameters and options"""
        return {
            'input_formats': self.available_input_formats,
            'output_formats': self.available_output_formats,
            'default_output': 'ionmix',
            'parameters': {
                'Znum': {
                    'description': 'Comma separated list of atomic numbers',
                    'example': '1,6',
                    'required': True
                },
                'Xfracs': {
                    'description': 'Comma separated list of element fractions',
                    'example': '0.5,0.5',
                    'required': True
                },
                'tabnum': {
                    'description': 'SESAME table number',
                    'example': '7592',
                    'required': False
                },
                'Tmin': {
                    'description': 'Minimum temperature filter (eV)',
                    'example': '0.1',
                    'required': False
                },
                'outname': {
                    'description': 'Output filename without extension',
                    'example': 'polystyrene_converted',
                    'required': False
                },
                'verbose': {
                    'description': 'Enable verbose output',
                    'type': 'boolean',
                    'default': True
                }
            }
        }
    
    def validate_parameters(self, params):
        """Validate conversion parameters"""
        errors = []
        
        # Check required parameters
        if 'Znum' not in params or not params['Znum']:
            errors.append("Atomic numbers (Znum) are required")
        else:
            try:
                znum_list = [int(z.strip()) for z in params['Znum'].split(',')]
                if any(z <= 0 for z in znum_list):
                    errors.append("All atomic numbers must be positive")
            except ValueError:
                errors.append("Invalid atomic numbers format")
        
        if 'Xfracs' not in params or not params['Xfracs']:
            errors.append("Element fractions (Xfracs) are required")
        else:
            try:
                xfracs_list = [float(x.strip()) for x in params['Xfracs'].split(',')]
                if any(x <= 0 for x in xfracs_list):
                    errors.append("All element fractions must be positive")
                if abs(sum(xfracs_list) - 1.0) > 1e-6:
                    errors.append("Element fractions should sum to 1.0")
            except ValueError:
                errors.append("Invalid element fractions format")
        
        # Check Znum and Xfracs have same length
        if 'Znum' in params and 'Xfracs' in params and params['Znum'] and params['Xfracs']:
            try:
                znum_list = params['Znum'].split(',')
                xfracs_list = params['Xfracs'].split(',')
                if len(znum_list) != len(xfracs_list):
                    errors.append("Number of atomic numbers must match number of fractions")
            except:
                pass  # Already caught above
        
        # Check optional parameters
        if 'tabnum' in params and params['tabnum']:
            try:
                int(params['tabnum'])
            except ValueError:
                errors.append("Table number must be an integer")
        
        if 'Tmin' in params and params['Tmin']:
            try:
                tmin = float(params['Tmin'])
                if tmin <= 0:
                    errors.append("Minimum temperature must be positive")
            except ValueError:
                errors.append("Minimum temperature must be a number")
        
        return errors
    
    def get_converter_status(self):
        """Get current status of conversion capabilities"""
        status = {
            'opacplot2_available': self.opacplot2_available,
            'hedp_available': self.hedp_available,
            'hedp_error': self.hedp_error,
            'conversion_possible': False,
            'limitations': []
        }
        
        if not self.opacplot2_available:
            status['limitations'].append("opacplot2 not available - no conversion possible")
        elif not self.hedp_available:
            status['limitations'].append(f"hedp not available - {self.hedp_error}")
            status['limitations'].append("Using opacplot2-only conversion method")
            status['conversion_possible'] = True  # Can still convert with opacplot2 alone
        else:
            status['conversion_possible'] = True
            
        return status
    
    def convert_file(self, input_file, output_dir, params, progress_callback=None):
        """
        Convert SESAME file using direct opacplot2 library approach
        
        Returns: (success, output_file_path, message)
        """
        try:
            # Check converter status first
            status = self.get_converter_status()
            if not status['conversion_possible']:
                return False, None, "Conversion not possible: " + "; ".join(status['limitations'])
            
            # Validate inputs
            if not os.path.exists(input_file):
                return False, None, f"Input file not found: {input_file}"
            
            if not os.path.exists(output_dir):
                return False, None, f"Output directory not found: {output_dir}"
            
            validation_errors = self.validate_parameters(params)
            if validation_errors:
                return False, None, f"Parameter validation failed: {'; '.join(validation_errors)}"
            
            if progress_callback:
                if self.hedp_available:
                    progress_callback("Loading SESAME file (full functionality)...")
                else:
                    progress_callback("Loading SESAME file (opacplot2-only mode)...")
            
            # Load SESAME file
            try:
                sesame_data = opp.OpgSesame(input_file, opp.OpgSesame.DOUBLE, verbose=False)
            except:
                try:
                    sesame_data = opp.OpgSesame(input_file, opp.OpgSesame.SINGLE, verbose=False)
                except Exception as e:
                    return False, None, f"Failed to load SESAME file: {str(e)}"
            
            # Get material ID
            material_ids = list(sesame_data.data.keys())
            if not material_ids:
                return False, None, "No material data found in SESAME file"
            
            material_id = material_ids[0]  # Use first material
            
            if progress_callback:
                progress_callback(f"Converting material {material_id}...")
            
            # Parse parameters
            znum_list = [int(z.strip()) for z in params['Znum'].split(',')]
            xfracs_list = [float(x.strip()) for x in params['Xfracs'].split(',')]
            
            # Optional parameters
            tabnum = int(params['tabnum']) if params.get('tabnum') else material_id
            filter_temps = float(params['Tmin']) if params.get('Tmin') else None
            
            # Set output name
            if params.get('outname'):
                output_name = params['outname']
            else:
                basename = os.path.splitext(os.path.basename(input_file))[0]
                output_name = f"{basename}_converted"
            
            output_file = os.path.join(output_dir, output_name + '.cn4')
            
            if progress_callback:
                progress_callback("Performing conversion...")
            
            # Convert to EoS dictionary
            eos_dict = sesame_data.toEosDict(
                Znum=znum_list,
                Xnum=xfracs_list,
                tabnum=tabnum,
                filter_temps=filter_temps
            )
            
            if progress_callback:
                progress_callback("Extracting ion number density from EoS data...")
            
            # Write IONMIX file using correct API
            # Extract required data from EoS dictionary
            zvals = eos_dict['Znum']  # Atomic numbers
            fracs = eos_dict['Xnum']  # Element fractions 
            numDens = eos_dict['idens']  # Ion number density grid (atoms/cm³) - direct from opacplot2
            temps = eos_dict['temp']    # Temperature grid
            
            # Extract optional EoS data if available
            optional_data = {}
            if 'Pi_DT' in eos_dict:
                optional_data['pion'] = eos_dict['Pi_DT']  # Ion pressure
            if 'Pec_DT' in eos_dict:
                optional_data['pele'] = eos_dict['Pec_DT']  # Electron pressure
            if 'Ui_DT' in eos_dict:
                optional_data['eion'] = eos_dict['Ui_DT']  # Ion energy
            if 'Uec_DT' in eos_dict:
                optional_data['eele'] = eos_dict['Uec_DT']  # Electron energy
            if 'Zf_DT' in eos_dict:
                optional_data['zbar'] = eos_dict['Zf_DT']  # Ionization state
            
            # Call writeIonmixFile with extracted data
            opp.writeIonmixFile(
                fn=output_file,
                zvals=zvals,
                fracs=fracs,
                numDens=numDens,
                temps=temps,
                **optional_data
            )
            
            if os.path.exists(output_file):
                file_size = os.path.getsize(output_file)
                if progress_callback:
                    progress_callback("Conversion completed successfully")
                return True, output_file, f"Conversion successful. Output file: {output_file} ({file_size/1024:.1f} KB)"
            else:
                return False, None, "Conversion completed but output file not found"
                
        except Exception as e:
            return False, None, f"Conversion error: {str(e)}"
    
    def get_suggested_parameters(self, material_info):
        """Get suggested parameters based on material information"""
        suggestions = {
            'Znum': '1,6',  # Default for organic materials like polystyrene
            'Xfracs': '0.5,0.5',
            'tabnum': str(material_info.get('material_id', '')),
            'Tmin': '',
            'outname': f"material_{material_info.get('material_id', 'converted')}"
        }
        
        # Adjust based on material properties
        if 'zmax' in material_info and material_info['zmax'] != 'N/A':
            try:
                zmax = float(material_info['zmax'])
                if zmax < 2:  # Hydrogen-like
                    suggestions['Znum'] = '1'
                    suggestions['Xfracs'] = '1.0'
                elif zmax < 4:  # Light elements
                    suggestions['Znum'] = '1,6'
                    suggestions['Xfracs'] = '0.5,0.5'
                elif zmax < 10:  # Medium elements
                    suggestions['Znum'] = '6'
                    suggestions['Xfracs'] = '1.0'
            except (ValueError, TypeError):
                pass  # Use defaults
        
        return suggestions
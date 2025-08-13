# Example Data

This directory is intended for sample data files for testing and demonstration purposes.

## Required Files (Not Included in Repository)

To test the application, you need to provide your own data files:

- `*.ses` - SESAME equation of state files
- `*.cn4` - CN4/IONMIX reference files (optional, for benchmark testing)

## Sample Data Suggestion

For testing purposes, you can use:
- **Material**: Polystyrene (SESAME table 7592)
- **Elements**: Hydrogen + Carbon
- **Test conversion**: `--Znum 1,6 --Xfracs .5,.5 --Tmin 0.1`

## Usage

Once you have obtained sample SESAME files:

1. **Load SESAME file**: Place `.ses` files in this directory and use the GUI to load them
2. **Test conversion**: Use the conversion feature to generate CN4 files
3. **Benchmark testing**: Compare generated files with reference implementations

## Command Line Equivalent

For reference, CN4 files can be generated using opac-convert:
```bash
opac-convert --Znum 1,6 --Xfracs .5,.5 --Tmin 0.1 your_file.ses
```

## Data Sources

SESAME data files can be obtained from:
- [Los Alamos National Laboratory](https://www.lanl.gov/projects/data/eos.html)
- Your institution's physics data repository
- Collaborative research projects

## Note

Data files are not included in this repository due to:
- **Size considerations**: SESAME files can be large (MB to GB)
- **Licensing**: Data may have specific usage restrictions
- **Version control**: Binary data files are not suitable for Git tracking

Please obtain appropriate SESAME data files according to your research needs and institutional access.
# Example Data

This directory contains sample data files for testing and demonstration purposes.

## Files

- `7592.ses` - Sample SESAME equation of state file (Polystyrene)
- `7592.cn4` - Reference CN4/IONMIX file generated from 7592.ses using opac-convert

## Usage

These files can be used to test the application functionality:

1. **Load SESAME file**: Use `7592.ses` to test the file loading and analysis features
2. **Conversion benchmark**: Use `7592.cn4` as a reference for conversion accuracy testing

## Command Line Equivalent

The reference CN4 file was generated using:
```bash
opac-convert --Znum 1,6 --Xfracs .5,.5 --Tmin 0.1 7592.ses
```

## Material Properties

- **Material**: Polystyrene (C₈H₈)
- **Elements**: Hydrogen (50%) + Carbon (50%)
- **SESAME Table ID**: 7592

These files are provided for testing purposes only and may not represent the most current or accurate data for production use.
# Contributing to SESAME EoS GUI

Thank you for your interest in contributing to SESAME EoS GUI! This document provides guidelines for contributing to the project.

## 🤝 How to Contribute

### Reporting Bugs
1. Check existing [issues](https://github.com/yourusername/sesame-eos-gui/issues) first
2. Create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - System information (OS, Python version)
   - Sample files (if applicable)

### Suggesting Features
1. Search existing feature requests
2. Create a new issue with:
   - Clear use case description
   - Expected behavior
   - Mockups or examples (if applicable)

### Code Contributions

#### Development Setup
```bash
git clone https://github.com/yourusername/sesame-eos-gui.git
cd sesame-eos-gui

# Install dependencies
python setup.py

# Run the application
python launch.py
```

#### Code Standards
- Follow PEP 8 style guidelines
- Add docstrings for functions and classes
- Include type hints where appropriate
- Write tests for new functionality

#### Software Engineering Principles
This project follows these core principles:
- **KISS (Keep It Simple, Stupid)**: Prefer simple, readable solutions
- **DRY (Don't Repeat Yourself)**: Avoid code duplication
- **SOLID Principles**: Especially Single Responsibility Principle
- **Documentation Sync**: Update docs with code changes

#### Pull Request Process
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes following the coding standards
4. Add or update tests as needed
5. Update documentation if required
6. Commit your changes: `git commit -m 'Add amazing feature'`
7. Push to the branch: `git push origin feature/amazing-feature`
8. Open a Pull Request

#### Pull Request Requirements
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex logic
- [ ] Documentation updated if needed
- [ ] Tests pass (if applicable)
- [ ] No merge conflicts

## 🧪 Testing

### Running Tests
```bash
# Test installation
python test_installation.py

# Test conversion functionality
python -c "from opac_converter import OPACConverter; print('Import successful')"
```

### Test Data
- Use small test files for development
- Do not commit large .ses files to the repository
- Sample files should be < 1MB

## 📚 Documentation

### Code Documentation
- Add docstrings to all public functions and classes
- Use Google-style docstrings
- Include parameter types and return values
- Provide usage examples

### User Documentation
- Update README.md for user-facing changes
- Update USAGE_SUMMARY.md for workflow changes
- Keep installation instructions current

## 🔄 Release Process

### Version Numbering
- Follow semantic versioning (MAJOR.MINOR.PATCH)
- Update version in README.md badges
- Update CHANGELOG.md

### Release Checklist
- [ ] Version bumped
- [ ] CHANGELOG.md updated
- [ ] Documentation updated
- [ ] Tests passing
- [ ] No debug code or temporary files

## 💬 Community Guidelines

### Communication
- Be respectful and professional
- Use clear, descriptive language
- Provide context and examples
- Help others when possible

### Issue Labels
- `bug`: Something isn't working
- `enhancement`: New feature or improvement
- `documentation`: Documentation needs
- `question`: Further information needed
- `help wanted`: Extra attention needed
- `good first issue`: Good for newcomers

## 🛠️ Development Tips

### Debugging
- Use the built-in logging functionality
- Test with various SESAME file formats
- Verify conversion accuracy with benchmark data

### Performance
- Profile code for large files
- Consider memory usage for big datasets
- Optimize visualization rendering

### Dependencies
- Minimize new dependencies
- Use established, well-maintained packages
- Consider compatibility with opacplot2 ecosystem

## 📞 Getting Help

- Open an issue for technical questions
- Check existing documentation first
- Provide minimal reproducible examples
- Tag relevant maintainers if needed

## 🙏 Recognition

Contributors will be acknowledged in the project documentation and release notes.

Thank you for helping improve SESAME EoS GUI!
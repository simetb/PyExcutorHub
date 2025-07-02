# 🤝 Contributing to PyExecutorHub

Thank you for your interest in contributing to PyExecutorHub! This document provides guidelines for contributing.

## 🚀 Quick Start

1. **Fork** the repository
2. **Clone** your fork: `git clone https://github.com/YOUR_USERNAME/PyExecutorHub.git`
3. **Create** a feature branch: `git checkout -b feature/amazing-feature`
4. **Make** your changes
5. **Test** your changes
6. **Commit** your changes: `git commit -m 'Add amazing feature'`
7. **Push** to your branch: `git push origin feature/amazing-feature`
8. **Open** a Pull Request

## 📋 Development Setup

### Prerequisites
- Python 3.11+
- Docker
- Docker Compose

### Local Development
```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/PyExecutorHub.git
cd PyExecutorHub

# Copy environment file
cp env.example .env

# Edit configuration
nano .env

# Start the development environment
docker compose up -d --build

# Test the API
curl http://localhost:8000/health
```

## 🧪 Testing

### Running Tests
```bash
# Test the API endpoints
curl http://localhost:8000/programs

# Test script execution
curl -X POST http://localhost:8000/execute \
  -H "Content-Type: application/json" \
  -d '{"program_id": "example_script"}'
```

### Code Quality
- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Add docstrings to functions and classes
- Keep functions small and focused

## 📝 Code Style

### Python
- Use **snake_case** for variables and functions
- Use **PascalCase** for classes
- Use **UPPER_CASE** for constants
- Maximum line length: 88 characters (Black formatter)

### Documentation
- Write clear, concise docstrings
- Use English for all comments and documentation
- Include examples in docstrings

### Git Commits
- Use conventional commit messages
- Format: `type(scope): description`
- Examples:
  - `feat(api): add new endpoint for program status`
  - `fix(docker): resolve container timeout issue`
  - `docs(readme): update installation instructions`

## 🐛 Bug Reports

When reporting bugs, please include:

1. **Environment**: OS, Python version, Docker version
2. **Steps to reproduce**: Clear, step-by-step instructions
3. **Expected behavior**: What you expected to happen
4. **Actual behavior**: What actually happened
5. **Logs**: Relevant error messages and logs
6. **Screenshots**: If applicable

## 💡 Feature Requests

When requesting features, please include:

1. **Problem description**: What problem does this solve?
2. **Proposed solution**: How should it work?
3. **Use cases**: Who would benefit from this?
4. **Alternatives considered**: What other approaches were considered?

## 🔧 Pull Request Guidelines

### Before Submitting
- [ ] Code follows the project's style guidelines
- [ ] Tests pass locally
- [ ] Documentation is updated
- [ ] No sensitive data is included
- [ ] Commit messages are clear and descriptive

### PR Description
- **Summary**: Brief description of changes
- **Motivation**: Why these changes are needed
- **Testing**: How to test the changes
- **Breaking Changes**: Any breaking changes and migration steps

## 📚 Documentation

### Adding Documentation
- Update README.md for user-facing changes
- Update docstrings for API changes
- Add examples for new features
- Include troubleshooting guides for complex features

### Documentation Standards
- Use clear, simple language
- Include code examples
- Add screenshots for UI changes
- Keep documentation up to date

## 🛡️ Security

### Reporting Security Issues
- **DO NOT** create a public issue for security vulnerabilities
- Email security issues to: [your-email@example.com]
- Include detailed information about the vulnerability
- Allow time for response before public disclosure

### Security Guidelines
- Never commit sensitive data (API keys, passwords, etc.)
- Use environment variables for configuration
- Validate all user inputs
- Follow security best practices

## 🏷️ Versioning

This project follows [Semantic Versioning](https://semver.org/):

- **MAJOR**: Incompatible API changes
- **MINOR**: New functionality in a backward-compatible manner
- **PATCH**: Backward-compatible bug fixes

## 📄 License

By contributing to this project, you agree that your contributions will be licensed under the MIT License.

## 🙏 Acknowledgments

- Thank you for contributing to PyExecutorHub!
- Your contributions help make this project better for everyone
- We appreciate your time and effort

---

**⚡ PyExecutorHub - Deploy Python scripts in seconds, execute with confidence.**

**Need help?** Open an issue or reach out to the maintainers! 
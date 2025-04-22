# Contributing to Smart Job Application Assistant

Thank you for considering contributing to Smart Job Application Assistant! This document provides guidelines and instructions for contributing to this project.

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for everyone.

## How Can I Contribute?

### Reporting Bugs

If you find a bug, please create an issue with the following information:

1. A clear, descriptive title
2. Steps to reproduce the issue
3. Expected behavior
4. Actual behavior
5. Any error messages or screenshots
6. Your environment (OS, Python version, etc.)

### Suggesting Enhancements

We welcome suggestions for improvements! When suggesting enhancements:

1. Use a clear, descriptive title
2. Provide a detailed description of the proposed enhancement
3. Explain why this enhancement would be useful
4. Include any relevant examples or mockups

### Pull Requests

1. Fork the repository
2. Create a new branch (`git checkout -b feature/your-feature-name`)
3. Make your changes
4. Run tests if available
5. Commit your changes (`git commit -m 'Add some feature'`)
6. Push to the branch (`git push origin feature/your-feature-name`)
7. Create a new Pull Request

## Development Setup

1. Clone your fork of the repository
2. Create a virtual environment and activate it
3. Install dependencies: `pip install -r requirements.txt`
4. Install development dependencies: `pip install -r requirements-dev.txt` (if available)
5. Run the application: `streamlit run app.py`

## Style Guidelines

### Python Code

- Follow PEP 8 guidelines
- Use descriptive variable names
- Include docstrings for functions and classes
- Keep functions small and focused on a single task

### Documentation

- Keep documentation up-to-date with code changes
- Use clear, concise language
- Include examples where appropriate

## Project Structure

- `app.py`: Main application file
- `openrouter_client.py`: OpenRouter API client
- `profile_converter.py`: Profile format conversion utilities
- `requirements.txt`: Package dependencies
- `README.md`: Project overview
- `SETUP_INSTRUCTIONS.md`: Detailed setup instructions
- `LICENSE`: MIT License
- `CONTRIBUTING.md`: Contribution guidelines

## Feature Ideas

Here are some features you might consider contributing:

1. **Profile Template Library**: Add more professional profile templates for different industries
2. **Skill Taxonomy**: Implement a standardized skill taxonomy for better matching
3. **Job Scraping**: Add support for scraping job listings directly from popular job sites
4. **Resume Export**: Allow exporting generated resumes in multiple formats (PDF, DOCX)
5. **AI Model Benchmarking**: Compare performance of different AI models for specific tasks
6. **Application Analytics**: Add visualizations for job application statistics
7. **Interview Preparation**: Generate possible interview questions based on job requirements

## Questions?

If you have any questions about contributing, please open an issue with your question.

Thank you for your contributions!
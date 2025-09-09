#!/usr/bin/env python3
"""
AI Proxy - Multi-Provider Claude Code Proxy
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="ai-proxy",
    version="1.0.0",
    author="AI Proxy Team",
    author_email="ai-proxy@example.com",
    description="A Flask-based proxy that allows Claude Code to use multiple AI providers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/agromanon/ai-proxy",
    project_urls={
        "Bug Tracker": "https://github.com/agromanon/ai-proxy/issues",
        "Documentation": "https://github.com/agromanon/ai-proxy#readme",
        "Source Code": "https://github.com/agromanon/ai-proxy",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "ai-proxy=app:main",
        ],
    },
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black>=21.0",
            "flake8>=3.8",
        ],
    },
)
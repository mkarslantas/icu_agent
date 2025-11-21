"""
ICU Agent - Multi-Agent System for ICU Patient Monitoring
Setup script for package installation
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

# Read requirements
requirements = []
with open("requirements.txt", "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#"):
            # Remove version constraints for setup.py
            requirements.append(line.split(";")[0].strip())

setup(
    name="icu-agent",
    version="1.0.0",
    author="ICU Agent Team",
    author_email="info@example.com",
    description="Multi-agent system for ICU patient monitoring and clinical decision support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/icu-agent",
    packages=find_packages(exclude=["tests", "tests.*", "docs", "examples"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Healthcare Industry",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "icu-agent=scripts.orchestrator:cli",
            "icu-monitor=scripts.monitor:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.yaml", "*.yml", "*.txt"],
    },
    zip_safe=False,
)

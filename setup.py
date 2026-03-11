"""Setup script for age-detector package."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="age-detector",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A tool to detect if people in images are underage (under 18)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/age-detector",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "age-detector=age_detector.cli:main",
            "age-detector-api=age_detector.api:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["models/*.caffemodel", "models/*.prototxt"],
    },
)

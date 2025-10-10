from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="mikrotik-backup-tool",
    version="1.0.0",
    author="MikroTik Backup Tool Team",
    author_email="support@mikrotik-backup-tool.com",
    description="A beautiful, web-based MikroTik router backup management system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/mikrotik-backup-tool",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: System :: Networking",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Framework :: Flask",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "mikrotik-backup=backend.app:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.html", "*.css", "*.js", "*.svg", "*.ico"],
    },
    keywords="mikrotik router backup automation flask web-interface",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/mikrotik-backup-tool/issues",
        "Source": "https://github.com/yourusername/mikrotik-backup-tool",
        "Documentation": "https://github.com/yourusername/mikrotik-backup-tool#readme",
    },
)

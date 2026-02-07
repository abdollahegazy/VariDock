from setuptools import setup, find_packages

setup(
    name="varidock",
    packages=find_packages(),
    version="0.1.2",
    description="Docker Automation",
    extras_require={
        "dev": [
            "pytest>=8",
            "ruff",
            "mypy",
            "pdoc",
            "build",
        ]
    },
)
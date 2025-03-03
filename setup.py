from setuptools import setup, find_packages

setup(
    name="ml3log",
    version="0.1.0",
    packages=find_packages(),
    description="A minimal logger and web server",
    author="Multinear",
    python_requires=">=3.8",
    package_data={
        "ml3log": ["templates/*.html"],
    },
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

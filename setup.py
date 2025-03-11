from setuptools import setup, find_packages

setup(
    name="ml3log",
    version="0.1.1",
    packages=find_packages(),
    description="A minimal logger and web server",
    author="Multinear",
    python_requires=">=3.8",
    package_data={
        "ml3log": ["static/*.html", "static/*.css", "static/*.js"],
    },
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "ml3log=ml3log.__main__:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

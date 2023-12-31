import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="class_config",
    version="0.0.1",
    author="Tanix",
    description="Python class as config.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/TanixLu/class_config",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

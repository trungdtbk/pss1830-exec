import setuptools
from pssexec.__version__ import VERSION

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pssexec",
    version=VERSION,
    author="Trung Truong",
    author_email="trungdtbk@gmail.com",
    description="Execute CLI or root commands on 1830 PSS nodes",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/trungdtbk/pss-1830-exec",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent"
    ],
    entry_points={
        'console_scripts' : ['pssexec=pssexec.pssexec:main']
    }
)

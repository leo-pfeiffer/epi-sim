from setuptools import setup, find_packages

setup(
    name="lib",
    version="1.0.0",
    packages=find_packages(),
    author="Leopold Pfeiffer",
    author_email="leopold.pfeiffer@icloud.com",
    description="A compartmental network model for COVID-19.",
    license="MIT",
    keywords=['epidemic', 'modelling'],
    url="",
    classifiers=[],
    python_requires=">=3.6",
)
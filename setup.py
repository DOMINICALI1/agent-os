from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="agentos-net",
    version="0.1.0",
    author="DOMINICALI1",
    description="A decentralized protocol for autonomous AI agent identity and negotiation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/DOMINICALI1/agent-os",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "grpcio>=1.50.0",
        "grpcio-tools>=1.50.0",
        "cryptography>=41.0.0",
        "protobuf>=4.21.0",
    ],
)
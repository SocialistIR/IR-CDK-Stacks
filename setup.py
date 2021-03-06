import setuptools


with open("README.md") as fp:
    long_description = fp.read()


setuptools.setup(
    name="ir_cdk_stacks",
    version="0.0.2",
    description="A framework for deploying incident response stacks for an AWS serverless infrastructure",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="author",
    package_dir={"": "ir_cdk_stacks"},
    packages=setuptools.find_packages(where="ir_cdk_stacks"),

    install_requires=["aws-cdk.core==1.35.0",],

    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Utilities",
        "Typing :: Typed",
    ],
)

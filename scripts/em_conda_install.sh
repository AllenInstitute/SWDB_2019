#!/bin/bash
# activate your conda environment of choice first
conda install -y -c conda-forge shapely itkwidgets k3d pykdtree pyembree
pip install -r https://gist.githubusercontent.com/fcollman/45285126b53cf03f01b2c2ff33705f00/raw/gistfile1.txt
pip install marshmallow==3.0.0rc6
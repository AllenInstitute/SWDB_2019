conda install -y -c conda-forge shapely itkwidgets k3d pykdtree
pip install -r https://gist.githubusercontent.com/fcollman/45285126b53cf03f01b2c2ff33705f00/raw/gistfile1.txt
git clone https://github.com/scopatz/pyembree.git
cd pyembree
conda install cython numpy
conda install -c conda-forge embree
set INCLUDE=%CONDA_PREFIX%\Library\include
set LIB=%CONDA_PREFIX%\Library\lib
python setup.py install --prefix=%CONDA_PREFIX%

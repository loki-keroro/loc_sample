程序步骤：
1.在磁盘根目录下新建文件夹，通过cmd新建一个python虚拟环境（python -m venv virtual_env）；
2.进入scripts激活环境后（activate），通过pip依次安装pyinstaller,numpy, gdal3.4.3(按numpy, gdal, pyinstaller的顺序安装不上pyinstaller)；
3.其中gdal需要去下载指定版本的whl（https://www.lfd.uci.edu/~gohlke/pythonlibs/#gdal），然后通过pip install XX.whl安装【https://blog.csdn.net/m0_47472749/article/details/124426544】；
4.打包完后，推出至虚拟环境根目录，将.py文件和虚拟环境放在一起后，通过”pyinstaller -F main.py“打包文件

注意：
失败版本：python 3.6 
安装顺序：conda环境下：gdal(自带) ,pyinstall

成功版本：python 3.8
安装顺序：numpy, gdal（3.6.2）, pyinstaller
解决打包后的exe过大问题（280->40M）
问题：直接在conda的虚拟环境下通过pyinstaller打包的exe文件过大（原因：在conda环境下打包，会把一些不必要的库也一同打包，造成exe过大）
#!/usr/bin/python
#-*- coding:cp936 -*-
import warnings
warnings.filterwarnings("ignore")
import os
# 对应自己的python包的安装地址
os.environ['PROJ_LIB'] = r'E:\Data_factory\virtual_env\Lib\site-packages\pyproj\proj_dir\share\proj'

import os

os.environ["TF_CPP_MIN_LOG_LEVEL"] = '3'  # 只显示 warning 和 Error


from osgeo import gdal, gdalconst
import os
import argparse

def coodToround(tranform,resolution):
    '''
    对转换信息中左上角坐标按条件进行取整
    :param tranform:转换信息
    :param resolution:图像分辨率
    :return:
    '''
    if resolution <1:
        tranform[0] = round(tranform[0] /0.25) * 0.25
        tranform[3] = round(tranform[3] / 0.25) * 0.25
    elif resolution ==1:
        tranform[0] = round(tranform[0] / 0.5) * 0.5
        tranform[3] = round(tranform[3] / 0.5) * 0.5
    elif resolution >1:
        tranform[0] = round(tranform[0])
        tranform[3] = round(tranform[3])

def GdalReprojectImage(srcFilePath, saveFolderPath, resampleFactor):
	"""
	栅格重采样
	:param srcFilePath:源文件路径
	:param saveFolderPath:输出路径
	:param resampleFactor:缩放比例
	:return:
	"""
	File_list = [os.path.join(srcFilePath, f) for f in os.listdir(srcFilePath) if f.endswith('.tif') or f.endswith('.img')]
	# File_list = [os.path.join(srcFilePath, f) for f in os.listdir(srcFilePath) if f.endswith('.tif')]
	for file in File_list:
		# 打开输入图像
		srcFileName = os.path.basename(file)
		name = os.path.splitext(srcFileName)[0]
		file_type = os.path.splitext(srcFileName)[-1]  ##获取文件后缀格式
		outFileName = name + str(resampleFactor) + file_type
		outFilePath = os.path.join(saveFolderPath, outFileName)
		if file_type == '.tif':
			driver = gdal.GetDriverByName('GTiff')
		else:
			gdal.SetConfigOption("HFA_USE_RRD", "YES")
			driver = gdal.GetDriverByName('HFA')

		dataset = gdal.Open(file, gdal.GA_ReadOnly)

		# 获取输入图像的投影、地理变换和波段数
		srcProjection = dataset.GetProjection()
		srcGeoTransform = dataset.GetGeoTransform()
		srcWidth = dataset.RasterXSize
		srcHeight = dataset.RasterYSize
		srcBandCount = dataset.RasterCount
		# srcNoDatas = [
		# 	dataset.GetRasterBand(bandIndex).GetNoDataValue()
		# 	for bandIndex in range(1, srcBandCount+1)
		# ]
		srcNoDatas=[256,256,256]

		srcBandDataType = dataset.GetRasterBand(1).DataType  #获取波段类型
		geoTransforms = list(srcGeoTransform)
		outWidth = int(srcWidth * geoTransforms[1]/resampleFactor)  #计算新的行列数
		outHeight = abs(int(srcHeight * geoTransforms[5]/resampleFactor))

		geoTransforms[1] = resampleFactor  #设置分辨率
		geoTransforms[5] = -resampleFactor

		# 设置投影坐标、地理变化参数
		outDataset = driver.Create(
			outFilePath,
			outWidth,
			outHeight,
			srcBandCount,
			srcBandDataType
		)

		#坐标取整
		coodToround(geoTransforms,resampleFactor)

		outGeoTransform = tuple(geoTransforms)
		outDataset.SetGeoTransform(outGeoTransform)
		outDataset.SetProjection(srcProjection)
		for bandIndex in range(1, srcBandCount+1):
			# print("正在写入" + srcFileName + " "+ str(bandIndex) + "波段;")
			data = dataset.GetRasterBand(bandIndex).ReadAsArray(buf_xsize=outWidth, buf_ysize=outHeight)
			band = outDataset.GetRasterBand(bandIndex)
			band.SetNoDataValue(srcNoDatas[bandIndex-1])
			band.WriteArray(data)
			band.FlushCache()
			band.ComputeBandStats(False)  # 计算统计信息

		gdal.ReprojectImage(dataset, outDataset, srcProjection, srcProjection,
							gdalconst.GRA_Bilinear,  #插值方式
							0.0, 0.0,
							)
		del dataset
		del outDataset
	print(f"完成文件夹内所有文件 {resampleFactor} m重采样！")
	return

if __name__ == "__main__":
	# ------------
	# args
	# ------------
	parser = argparse.ArgumentParser()
	# parser.add_argument('--srcimg_file', type=str, required=True,
	# 				  help='input image file path')
	# parser.add_argument('--tagimg_file', type=str, required=True,
	# 				help='input images file saving path')
	# parser.add_argument('--resample_res', type=float, required=True, default=2, help='Resolustion:0.5, 1, 2')
	parser.add_argument('--srcimg_file', type=str, required=False, default=r'E:\Data_factory\test_data\source_img',
					  help='input image file path')
	parser.add_argument('--tagimg_file', type=str, required=False, default=r'E:\Data_factory\test_data\target_img',
					help='input images file saving path')
	parser.add_argument('--resample_res', type=float, required=False, default=2, help='Resolustion:0.5, 1, 2')
	args = parser.parse_args()
	GdalReprojectImage(args.srcimg_file, args.tagimg_file, args.resample_res)


	# input("please input any key to exit!")
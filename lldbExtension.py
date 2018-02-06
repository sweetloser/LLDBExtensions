#!/usr/bin/python
#coding:utf-8

import lldb
import imp
import os


def __lldb_init_module(debugger,dict):
	filePath = os.path.realpath(__file__)
	fileDirPath = os.path.dirname(filePath)

	commandsDirPath = os.path.join(fileDirPath,'Commands')

	cmd = 'command script import '
	for file in os.listdir(commandsDirPath):
		fileName,fileExtension = os.path.splitext(file)
		if fileExtension == '.py':
			#如果文件后缀为py，则import
			fullPath = os.path.join(commandsDirPath,file)
			debugger.HandleCommand(cmd + fullPath)





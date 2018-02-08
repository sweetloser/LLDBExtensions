#!/usr/bin/python
#coding:utf-8

import lldb
import shlex
import optparse

def __lldb_init_module(debugger,internal_dict):
	debugger.HandleCommand("command script add -f %s.findImage sl_findImage" % (__name__))
	print "sl_findImage is ready."

def findImage(debugger,command,result,dict):
	# 解析参数
	usage = 'usage: %prog [options]'
	parser = optparse.OptionParser(prog='sl_findImage',usage=usage)
	parser.add_option('-i','--image',type='string',dest='image',help='The image to be found.')

	commandList = shlex.split(command)
	try:
		(options, args) = parser.parse_args(commandList)
	except Exception as e:
		print e
		return
	target = debugger.GetSelectedTarget()
	#如果没有输入参数，则默认是可执行文件模块
	if options.image == None:
		options.image = target.executable.basename

	for module in target.modules:
		# print module
		if module.file.basename == options.image:
			print "PATH:\t" + module.file.fullpath
			print "ASLR:\t"+str(hex(module.GetObjectFileHeaderAddress().GetLoadAddress(target)))
			return
			
	print "not found image named %s" % (options.image)




#!/usr/bin/python
#coding:utf-8

import lldb
import shlex
import optparse
import struct

def __lldb_init_module(debugger,internal_dict):
	#模块初始化
	debugger.HandleCommand('command script add -f %s.decryptDump decryptDump' % (__name__))
	print "DecryptDump is ready."


	
def decryptDump(debugger,command,result,dict):

	MH_MAGIC = 0xFEEDFACE
	MH_CIGAM = 0xCEFAEDFE

	MH_MAGIC_64 = 0xFEEDFACF
	MH_CIGAM_64 = 0xCFFAEDFE

	LC_ENCRYPTION_INFO = 0x21
	LC_ENCRYPTION_INFO_64 = 0x2C
	MACHO_HEADER_SIZE = 28
	MACHO_HEADER_SIZE_64 = 32

	# 解析参数
	usage = 'usage: %prog [options]'
	parser = optparse.OptionParser(prog='decryptDump',usage=usage)
	parser.add_option('-i','--image',type='string',dest='image',help='The image to be decrypted.')
	parser.add_option('-o','--output',type='string',dest='output',help='The decrypted file store path.')

	commandList = shlex.split(command)
	try:
		(options, args) = parser.parse_args(commandList)
	except Exception as e:
		print e
		return


	if options.output == None:
		raise Exception("No specified output path,Please use -h to see the instructions.");
	elif options.image == None:
		raise Exception("No module specified,Please use -h to see the instructions.");

	target = debugger.GetSelectedTarget()

	for module in target.modules:
		# print module
		if module.file.basename == options.image:

			image_load_address = module.GetObjectFileHeaderAddress().GetLoadAddress(target)
			print "INFO: image `%s` loaded at <0x%016x>" % (options.image,image_load_address)

			process = target.GetProcess();
			read_res = lldb.SBError()
			macho_memory = process.ReadMemory(image_load_address, 24, read_res)

			prefix = ""
			mach_header_size = 0x0
			encryption_info_cmd = LC_ENCRYPTION_INFO
			encryption_info_description = "LC_ENCRYPTION_INFO"
			cryptoffset = 0
			cryptsize = 0
			cryptid = 0

			if read_res.Success():
				magic, = struct.unpack("<I", macho_memory[0:4])

				print "%x" % (magic)
				print "%x" % (MH_MAGIC_64)

				if magic==MH_MAGIC or magic==MH_MAGIC_64:
					#小端
					prefix = '<'
				elif magic==MH_CIGAM or magic==MH_CIGAM_64:
					#大端
					prefix = '>'
				else:
					raise Exception("magic error ===> [0x%4x]" % (magic))

				#64bit
				if magic==MH_CIGAM_64 or magic==MH_MAGIC_64:
					mach_header_size = MACHO_HEADER_SIZE_64
					encryption_info_cmd = LC_ENCRYPTION_INFO_64
					encryption_info_description = 'LC_ENCRYPTION_INFO_64'

				#读取`ncmds`和`sizecmds`
				ncmds,sizecmds = struct.unpack(prefix + '2I', macho_memory[16:24])
				macho_memory = process.ReadMemory(image_load_address, sizecmds+mach_header_size, read_res)
				load_command_start = mach_header_size

				#读取各个`loadcommand`,寻找 `LC_ENCRYPTION_INFO` 或 `LC_ENCRYPTION_INFO_64`
				for i in range(ncmds):

					cmd, cmdsize = struct.unpack(prefix + '2I', macho_memory[load_command_start:load_command_start+8])
					if cmd == encryption_info_cmd:
						load_command_start = load_command_start + 8
						cryptoffset,cryptsize,cryptid = struct.unpack(prefix + '3I',macho_memory[load_command_start:load_command_start+12]);
						print "INFO: cryptoffset: 0x%04x\n      cryptsize: 0x%04x\n      cryptid: 0x%04x\n" % (cryptoffset,cryptsize,cryptid)
						
						break;

					else:
						load_command_start = load_command_start + cmdsize

				ci = debugger.GetCommandInterpreter()
				res = lldb.SBCommandReturnObject()
				ci.HandleCommand("memory read --force --outfile %s --binary --count %d 0x%016X" % (options.output, cryptsize, image_load_address + cryptoffset), res)
				if res.Succeeded():
					print "INFO: 0x%4x bytes read as binary" % (cryptsize)
				else:
					print res
			else:
				#读取错误
				print read_res

			#找到了相对应的模块，直接返回
			break






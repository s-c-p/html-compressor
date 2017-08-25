"""
	merge webpage and its associated folder into a single unit to reduce
	clutter on hardisk and avoid false positives in duplicate file scans
"""

import os
import sys
import shlex
import shutil
import zipfile
import contextlib
import subprocess
from concurrent.futures import ThreadPoolExecutor

EXTN = ".htmz"

if sys.platform == "Win32":
	starter = os.startfile
else:
	starter = lambda x: subprocess.run(f"xdg-open {x}", shell=True)

@contextlib.contextmanager
def rmdir_when_done(dir_name):
	""" dir_name be abspath """
	transient_path = dir_name.replace("_files", "")
	yield transient_path
	shutil.rmtree(dir_name)
	return

def get7z():
	ps = [
		r"C:\Program Files\7-Zip\7z.exe",
		r"C:\Program Files (x86)\7-Zip\7z.exe",
		"7zr"
	]
	for p in ps:
		try:	ans = subprocess.run(p, stdout=subprocess.PIPE)
		except:	pass
		else:
			if ans.stdout.startswith(b"\n7-Zip"):
				return p
	raise RuntimeError("Failed to locate 7-Zip exeutable")

def _run_7z(transient_path, resrcDirPath, srcPath=None):
	if srcPath:
		head = "HTM--- "
		fileDirList = resrcDirPath + '" "' + srcPath
	else:# if incomplete:
		head = "(incomplete) HTM--- "
		fileDirList = resrcDirPath
	a = os.path.dirname(transient_path)
	b = head + os.path.basename(transient_path) + EXTN
	archivePath = os.path.join(a, b)
	with zipfile.ZipFile(archivePath, "w") as zfh:
		if srcPath:
			??? op.relpath or
			??? op.basename(srcPath)
			zfh.write(srcPath)
		zfh.write(resrcDirPath)
		# for r, d, f in os.walk()
	# exer = get7z()
	# cmnd = f'{exer} a -tZIP -mx=0 "{archivePath}" "{fileDirList}"'
	# print(cmnd);	input();
	# subprocess.run(shlex.split(cmnd), stdout=subprocess.DEVNULL)
	return

def completeCompress(transient_path, resrcDirPath, srcPath):
	_run_7z(transient_path, resrcDirPath, srcPath)
	return

def incompleteCompress(transient_path, resrcDirPath):
	_run_7z(transient_path, resrcDirPath)
	return

def decide_n_compress(dir_of_a_webpage):
	with rmdir_when_done(dir_of_a_webpage) as file_name_prefix:
		if os.path.isfile(file_name_prefix + ".htm"):
			assoc_file_name = file_name_prefix + ".htm"
		elif os.path.isfile(file_name_prefix + ".html"):
			assoc_file_name = file_name_prefix + ".html"
		else:
			assoc_file_name = None
		# ----------------------------------------------------------------
		if assoc_file_name:
			completeCompress(file_name_prefix, dir_of_a_webpage, assoc_file_name)
			os.remove(assoc_file_name)
		else:
			incompleteCompress(file_name_prefix, dir_of_a_webpage)
	return

def compress(targetDir):
	targetDir = os.path.abspath(targetDir)
	for root, dirs, files in os.walk(targetDir):
		dirs = [x for x in dirs if x.endswith("_files")]
		dirs = [os.path.join(root, x) for x in dirs]
		# inside for loop to ensure recursive-ly found webpages are also
		# cleaned.
		for _ in dirs:    decide_n_compress(_)
		# obsolete, multi threaded approach
		# with ThreadPoolExecutor(max_workers=4) as manyThreads:
		# 	manyThreads.map(decide_n_compress, dirs)
	return

def main(dirList):
	for aDir in dirList:
		# print("{} - {}".format(i, j))
		compress(aDir)
		starter(aDir)
	return

if __name__ == '__main__':
	main(sys.argv[1:])

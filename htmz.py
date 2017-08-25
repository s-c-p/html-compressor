"""
	merge webpage and its associated folder into a single unit to reduce
	clutter on hardisk and avoid false positives in duplicate file scans
	TODO: make compress() multithreaded
	TODO: pause execution for large folder warning
"""

import os
import sys
import shutil
import zipfile
import subprocess
import contextlib

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

def runZipper(transient_path, resrcDirPath, srcPath=None):
	# derive the appropriate archivePath first
	head = "HTM--- " if srcPath else "(incomplete) HTM--- "
	a = os.path.dirname(transient_path)
	b = head + os.path.basename(transient_path) + EXTN
	archivePath = os.path.join(a, b)
	# and now do the compression
	# NOTE this could be done with contextmanager handling dir change
	# but doing so would take away the possibility of making this app
	# multithreaded
	with zipfile.ZipFile(archivePath, "w") as zfh:
		# decide ref point for relpath
		new_home = os.path.dirname(resrcDirPath)
		for r, d, files in os.walk(resrcDirPath):
			for f in files:
				locn_on_disk = os.path.join(r, f)
				locn_on_arcv = os.path.relpath(locn_on_disk, new_home)
				zfh.write(filename=locn_on_disk, arcname=locn_on_arcv)
			# if there ara any empty dirs (like ..._files/assets/apple) which
			# are empty then they are not written (hence lost) in zip file
			# although there is no point in preserving empty folders since
			# it isn;t refrenced by any code or has any assets but still we
			# will try to preserve it, maybe JUST maybe the name of folder
			# carries some SPECIAL significance
		# if .htm* exists, write it at root
		if srcPath:
			zfh.write(filename=srcPath, arcname=os.path.basename(srcPath))
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
			runZipper(file_name_prefix, dir_of_a_webpage, assoc_file_name)
			os.remove(assoc_file_name)
		else:
			runZipper(file_name_prefix, dir_of_a_webpage)
	return

def compress(targetDir: str):
	targetDir = os.path.abspath(targetDir)
	for root, dirs, files in os.walk(targetDir):
		# inside for loop to ensure recursive-ly found webpages are also
		# cleaned.
		endswith_files = lambda x: x.endswith("_files")
		build_abs_path = lambda x: os.path.join(root, x)
		dirs = filter(endswith_files, dirs)
		dirs = map(build_abs_path, dirs)
		for _ in dirs:
			decide_n_compress(_)
	return

def main(dirList: list):
	for aDir in dirList:
		# print("{} - {}".format(i, j))
		compress(aDir)
		try:	starter(aDir)
		except:	pass
	return

if __name__ == '__main__':
	main(sys.argv[1:])

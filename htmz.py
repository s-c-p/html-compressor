"""
	merge webpage and its associated folder into a single unit to reduce
	clutter on hardisk and avoid false positives in duplicate file scans
"""

import os
import sys
import shlex
import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor

EXTN = ".htmz"

if sys.platform == "Win32":
	starter = os.startfile
else:
	starter = lambda x: subprocess.run(f"xdg-open {x}", shell=True)

class Archive:
	name = str()
	absLocn = str()

class WebPage:
	htmlFile = str()
	contentsDir = str()

class PageZipper:
	"""
		class to handle zip.STOREing webpage's directory and associated
		file as supplied
	"""

	def __init__(self, webpageTitle):
		""" webpageTitle =>
		path to dir name with which webpage was saved, sans extn, sans _files
		part; e.g. `D:/research/diy-freeduino` no "_files" or ".htm*" in the
		end
		"""
		self.webpageTitle = webpageTitle
		self._derive()
		return

	def _derive(self):
		self.archive = Archive()
		self.archive.name = os.path.basename(self.webpageTitle)
		self.archive.absLocn = os.path.dirname(self.webpageTitle)
		self.webPage = WebPage()
		# we can't conclude webPage.htmlFile yet becuz EXTN is not none
		self.webPage.contentsDir = self.webpageTitle + "_files"
		return

	def _run_7z(self, incomplete=False):
		head = "(incomplete) HTM--- " if incomplete else "HTM--- "
		# implicit type-conversion below, archive changes from Archive() to str
		location = self.archive.absLocn
		file_name = head + self.archive.name + EXTN
		self.archive = os.path.join(location, file_name)
		# make string based on webpage contents
		if self.webPage.htmlFile:
			x1 = self.webPage.htmlFile
			x2 = self.webPage.contentsDir
			fileDirList = r'{}" "{}'.format(x1, x2)
			del x1, x2
		else:
			fileDirList = self.webPage.contentsDir
		exer = get7z()
		cmnd = f'{exer} a -tZIP -mx0 "{self.archive}" "{fileDirList}"'
		subprocess.run(shlex.split(cmnd), stdout=subprocess.DEVNULL)
		try:
			shutil.rmtree(self.webPage.contentsDir)
		except OSError:
			starter(os.path.dirname(self.webPage.contentsDir))
		# deletion of .htm is taken care by calling function completeCompress
		# since incompleteCompress doesn't need it
		return

	def incompleteCompress(self):
		self._run_7z(incomplete=True)
		return

	def completeCompress(self, ext):
		self.webPage.htmlFile = self.webpageTitle + ext
		self._run_7z()
		# os.remove(self.webPage.htmlFile)
		return


def decide_n_compress(aDir):
	if os.path.isfile(aDir+".htm"):
		PageZipper(aDir).completeCompress(".htm")
	elif os.path.isfile(aDir+".html"):
		PageZipper(aDir).completeCompress(".html")
	else:
		PageZipper(aDir).incompleteCompress()
	return

def completeCompress(archivePath, srcPath, resrcDirPath):
	return

def incompleteCompress():
	pass

@contextlib.contextmanager
def rmdir_when_done(dir_name):
	""" dir_name be abspath """
	file_name_prefix = dir_name.replace("_files", "")
	yield file_name_prefix
	shutil.rmtree(dir_name)
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
			completeCompress(file_name_prefix, assoc_file_name, dir_name)
			os.remove(assoc_file_name)
		else:
			incompleteCompress(file_name_prefix, dir_name)
	return

def compress(targetDir):
	targetDir = os.path.abspath(targetDir)
	for root, dirs, files in os.walk(targetDir):
		dirs = [x for x in dirs if x.endswith("_files")]
		dirs = [os.path.join(root, x) for x in dirs]
		dirs = [x.replace("_files", '') for x in dirs]
		# inside for loop to ensure recursive-ly found webpages are also
		# cleaned.
		# with ThreadPoolExecutor(max_workers=4) as manyThreads:
		# 	manyThreads.map(decide_n_compress, dirs)
		# obsolete, single threaded approach
		for _ in dirs:    decide_n_compress(_)
	return

def main(dirList):
	for aDir in dirList:
		# print("{} - {}".format(i, j))
		compress(aDir)
		starter(aDir)
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

if __name__ == '__main__':
	main(sys.argv[1:])

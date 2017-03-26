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

op = os.path

EXTN = ".htmz"
ZIP = r'"C:\Program Files\7-Zip\7z.exe" a -tZIP -mx0 "{archiveName}" "{fileList}"'

_silentExec = lambda string: subprocess.run(
		shlex.split(string), stdout=subprocess.DEVNULL
	)

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
		self.archive.name = op.basename(self.webpageTitle)
		self.archive.absLocn = op.dirname(self.webpageTitle)
		self.webPage = WebPage()
		# we can't conclude webPage.htmlFile yet becuz EXTN is not none
		self.webPage.contentsDir = self.webpageTitle + "_files"
		return

	def _run_7z(self, incomplete=False):
		head = "(incomplete) HTM--- " if incomplete else "HTM--- "
		# implicit type-conversion below, archive changes from Archive() to str
		location = self.archive.absLocn
		file_name = head + self.archive.name + EXTN
		self.archive = op.join(location, file_name)
		del location, file_name
		# make string based on webpage contents
		if self.webPage.htmlFile:
			x1 = self.webPage.htmlFile
			x2 = self.webPage.contentsDir
			fileDirList = r'{}" "{}'.format(x1, x2)
			del x1, x2
		else:
			fileDirList = self.webPage.contentsDir
		cmnd = ZIP.format(archiveName=self.archive, fileList=fileDirList)
		_silentExec(cmnd)
		try:
			shutil.rmtree(self.webPage.contentsDir)
		except OSError:
			os.startfile(op.dirname(self.webPage.contentsDir))
		# deletion of .htm is taken care by calling function completeCompress
		# since incompleteCompress doesn't need it
		return

	def incompleteCompress(self):
		self._run_7z(incomplete=True)
		return

	def completeCompress(self, ext):
		self.webPage.htmlFile = self.webpageTitle + ext
		self._run_7z()
		os.remove(self.webPage.htmlFile)
		return


def decide_n_compress(aDir):
	if op.isfile(aDir+".htm"):
		PageZipper(aDir).completeCompress(".htm")
	elif op.isfile(aDir+".html"):
		PageZipper(aDir).completeCompress(".html")
	else:
		PageZipper(aDir).incompleteCompress()
	return

def compress(targetDir):
	targetDir = op.abspath(targetDir)
	for root, dirs, files in os.walk(targetDir):
		dirs = [x for x in dirs if x.endswith("_files")]
		dirs = [op.join(root, x) for x in dirs]
		dirs = [x.replace("_files", '') for x in dirs]
		# inside for loop to ensure recursive-ly found webpages are also
		# cleaned.
		# with ThreadPoolExecutor(max_workers=4) as manyThreads:
		# 	manyThreads.map(decide_n_compress, dirs)
		# obsolete, single threaded approach
		for _ in dirs:    decide_n_compress(_)
	os.startfile(targetDir)
	return

def main(processList):
	for i, j in enumerate(processList):
		# print("{} - {}".format(i, j))
		compress(j)

if __name__ == '__main__':
	main(sys.argv[1:])


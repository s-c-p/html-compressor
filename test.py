import os
import uuid
import shutil

import htmz

class TestFailed(Exception):
	""" a nice looking wrapper to tell test failed """
	pass

temp_dir = str(uuid.uuid4())
shutil.copytree("test-files", temp_dir)

htmz.compress(temp_dir)
os.chdir(temp_dir)

for r, d, f in os.walk("."):
	if any([_.endswith("_files") for _ in d]):
		raise TestFailed

os.chdir("..")

shutil.rmtree(temp_dir)

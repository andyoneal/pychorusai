import setuptools

with open("README.md", "r") as d:
	long_description = d.read()


setuptools.setup(
	 name='pychorusai',  
	 version='0.2.3',
	 author="Andy O'Neal",
	 author_email="andyoneal@me.com",
	 license="MIT",
	 description="API wrapper for chorus.ai",
	 long_description=long_description,
     long_description_content_type="text/markdown",
	 url="https://github.com/andyoneal/pychorusai",
	 packages=setuptools.find_packages(),
	 install_requires=['requests','python-dateutil']
 )
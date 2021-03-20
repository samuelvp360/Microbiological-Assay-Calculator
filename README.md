# Microbiological Assay Calculator
A python built application to process the common calculations done in microbiology 

## Installation
### Linux
#### Using .spec file
1. Download MainController.spec file
2. Create and activate a virtual environment using conda or venv e.g.:
```bash
$ conda create -n MAC_env
$ conda activate MAC_env
```
3. Install pip:
```bash
$ conda install -c anaconda pip
```
4. Install dependencies using pip:
```bash
$ pip install matplotlib pandas PyQt5 ZODB pyinstaller
```
5. Build the dist package using pyinstaller and the .spec file
```bash
$ pyinstaller svp_mac.spec
```
6. Find the executable bin file and give it execution permit:
```bash
$ cd dist/Microbiological_Assay_Calculator/
$ sudo chmod +x svp_mac
```
7. Execute the binary:
```bash
$ ./svp_mac
```
<!--8. (Optional) Install the binary to execute it in terminal
```bash
$ sudo ln -s absolute/path/to/your/binFile/svp_mac /usr/bin/svp_mac 
```
-->

## Usage
### Linux
If you have compiled the binary file you can run it through the terminal
```bash
$ ./svp_mac
```
If not, you can run the source code MainController.py using python 3.x and the suitable environment with the installed dependencies: matplotlib, pandas, numpy, PyQt5 and ZODB.
```bash
$ python MainController.py
```
### Windows
Execute the .exe file just double clicking.

## Features
* Storing persistently all your Microbiological assays in the same place, as well as the different samples from each one.
* Easy adding and handling of the data from the reading of Microplates.
* Dynamic plotting of available samples using embeded PyQt5 Matplotlib backend.

## License
All rights reserved.

# Movelister

Movelister is a tool for creating various types of in-depth notes
about video game mechanics data in sheet form. This could include simple
move lists, detailed mechanics notes for glitchers or other type of tables which
model the limits of a game's potential interactivity.

**Movelister is still a work in progress and not ready for use.**

## Table of Contents

<!-- vim-markdown-toc GFM -->

* [How It Works](#how-it-works)
* [Dependencies](#dependencies)
* [How To Use](#how-to-use)
* [Development](#development)
  * [Linux (Ubuntu and Arch)](#linux-ubuntu-and-arch)
    * [Running Macros From LibreOffice](#running-macros-from-libreoffice)
    * [Running Macros From Separate Python Process](#running-macros-from-separate-python-process)
  * [Windows](#windows)
* [Testing](#testing)
  * [Running Tests](#running-tests)
* [Making Release Document](#making-release-document)
* [Resources](#resources)

<!-- vim-markdown-toc -->

## How It Works

Movelister is implemented on LibreOffice Calc (spreadsheet) and is used with
Python macros. Macros call further Python code which is responsible for
manipulating tables and sheets underneath.

## Dependencies

It's necessary for the user to install LibreOffice 5 or newer and Python 3.x to
be able to use the Movelister scripts. Movelister is tested to be working on
both Linux and Windows. Python is typically automatically included in a
LibreOffice installation on Windows but not always on Linux. If LibreOffice
Python support is missing on Linux, you need install LibreOffice Python support
packages separately. On Windows Python is located with regular installation. For
instance `C:\Program Files\LibreOffice
5\program\python-core-3.5.0\bin\python.exe`. On Ubuntu install following
packages to enable Python for LibreOffice:

```
sudo apt install libreoffice-script-provider-python uno-libs3 python3-uno
```

On Linux distros that has both Python 2 and 3 versions available and command
`python` points to Python 2. Developers can change `python` commands to
`python3` in this readme instead.

Arch installation has been tested to work out of the box.

## How To Use

Project is released as a LibreOffice document which has all project sources
embedded inside of it. So no additional installations needed. Just grab the
movelister document under `releases` folder and you are good to go.

## Development

To have a good development environment and with debugging abilities. It's
easier to develop scripts using a separate Python process which then connects to
an external LibreOffice process using sockets. After you are done with the
development, you can run working scripts inside the LibreOffice process. [This
Christopher Bourez's blog post](http://christopher5106.github.io/office/2015/12/06/openoffice-libreoffice-automate-your-office-tasks-with-python-macros.html)
explains the idea and this same idea is used with this project.

Movelister is developed so that is support running macros from separate Python
process and from the LibreOffice itself. When running macros from separate
Python process, it doesn't matter where Movelister project is located because
Python connects to LibreOffice process through socket. When running macros from
LibreOffice itself, you need to tell LibreOffice where to find them. Easiest way
to do this is clone Movelister to your wanted location where you normally do
your development and then make symbolic link from LibreOffice user Python macros
folder to Movelister folder. This varies a little bit between the platforms and
is explained below for each platform.

### Linux (Ubuntu and Arch)

#### Running Macros From LibreOffice

LibreOffice user Python macros are located under
`~/.config/libreoffice/4/user/Scripts/python/`. This still holds true if you are
using LibreOffice version 6 and above. If you only have
folders up to `.../user/` then you can make folders `Scripts` and `python` with
`mkdir` program. After this `cd` into just created python folder. Your path now
should be something like this:
`/home/kazooie/.config/libreoffice/4/user/Scripts/python`. Now make symbolic
link to cloned Movelister folder with following and change `path_to_movelister`
to point to your cloned Movelister folder:

```
ln -s <path_to_movelister> movelister
```

Now in LibreOffice when you go to **Tools -> Macros -> Run Macro** and open **My
Macros**. You should see **movelister** as a listed macro package. Now open
**movelister** and select **main**. Then on the right you should see list of all
available macros which can be executed or mapped to keys.

#### Running Macros From Separate Python Process

In project root folder, start LibreOffice Calc process with:

```
libreoffice templates/movelister_test.ods --accept="socket,host=localhost,port=2002;urp"
```

This opens socket with port 2002 which Python process then connects. Then start
a separate Python process by running `main.py` with:

```
python main.py
```

This script should run without errors. If you see error messages, make sure the
socket is open or follow error message instructions.

### Windows

TODO: Write this again with better guidelines. To use LibreOffice Calc with a

socket open, you have to start LibreOffice using the parameter listed below.
For convenience's sake, you might want to include this parameter inside some
shortcut that starts LibreOffice.

```
--accept="socket,host=localhost,port=2002;urp"
```

If you use command line to run scripts, it's the easiest to just use
LibreOffice's own installed version of Python to run any Python scripts.
Otherwise Python may have difficulties finding the important UNO library. In
addition, you need to start running the scripts from the main Movelister
directory so that Python can find any related Movelister-modules as well.

This part of the process can be made a bit faster by writing an own .bat file
inside the Movelister main folder that starts main.py with LibreOffice's own
Python executable that's usually situated in *LibreOffice 5/Program/*. For
example:

```
..\..\..\..\program\python main.py
```

## Testing

Movelister has unit tests to test application functionality and is implemented
using Python's own [unittests](https://docs.python.org/3/library/unittest.html)
library and tests can be found under `test` folder of the project.

During testing Python process will spawn headless LibreOffice Calc process
accepting socket connections. This connection is then used with UNO API to
communicate with LibreOffice process to verify application functionality.
During testing Python will instruct LibreOffice to reload the file between test
cases.

NOTE: Unit tests works on Linux but not fully on Windows. When you run all unit
tests on Windows, LibreOffice will show a dialog between test cases that the
file is already open and do you want to open file in read-only mode. When file
is opened in the read-only mode then tests that write data over UNO API will
fail to do so. And as a result unit test will report an error saying it didn't
see the data it was trying to write over UNO API. This read-only error when
reopening the file between test cases doesn't exist on Linux and no workaround
for this has been found yet. Running single unit test at the time on Windows
should work fine though.

### Running Tests

Before running tests you need to set `MV_LB_BIN` environment variable to point
to the LibreOffice executable. This is used to run LibreOffice during test. On
Linux for example:

```
export MV_LB_BIN="libreoffice"
```

and on Windows:

```
set MV_LB_BIN="C:\Program Files\LibreOffice 5\program\soffice.exe"
```

How to run tests depends your system you are using. With Linux LibreOffice is
using system's Python installation and on Windows LibreOffice comes with it's
own Python executable. On Linux you can just go to the project's root and run
tests with system's Python:

```
python -m unittest
```

Unfortunately on Windows things are not so simple.  On Windows you need to use
LibreOffice's own Python executable instead. This executable is located under
LibreOffice installation folder. From project's root you need to traverse path
to the LibreOffice Python executable and this path depends where you cloned this
project. In this case it might be easier to make a command line bat script to
run the tests. For example something like the following:

```
..\..\..\..\program\python.exe -m unittest
```

## Making Release Document

It's possible to pack Python source files be part of the LibreOffice document.
This way when file is shared the sources come with it. So no system installation
needed.

LibreOffice files are like zip files which consist of files and metadata xml
file named `manifest.xml`. This file contains list of paths of all files inside
the document. When Python source files are added to the document, manifest.xml
file also need to be edited to include paths of added files. If path is missing
then LibreOffice will not find the file. All Python files need to be placed
under `Scripts/python` subfolder of the document.

To automate above process project includes Python scripts which will do the
heavy lifting. All scripts are located under `scripts` folder of the project.

In Movelister making final release document is a two step process. First
`release_base.ods` file is created which includes only dummy Python macros that
doesn't do anything. This document is then used to manually assign macros to
buttons in the document. To make `release_base.ods` file run:

```
python scripts/make_release_base.py
```

After buttons are assigned manually, the actual release can be made from
`release_base.ods`.  In this stage all source files are packed into the final
document and its `manifest.xml` modified to include source file paths. Also the
file including dummy macros is replaced with the real one. To make a release
document run:

```
python scripts/make_release.py
```

This will make a new movelister LibreOffice document under `releases` folder
which is ready to use. If you are interested how packing process works take a
look at files inside the `scripts` folder.

## Resources

* [LibreOffice Python Scripts Help](https://help.libreoffice.org/6.3/en-US/text/sbasic/python/main0000.html)
* [LibreOffice Wiki of Python applications](https://wiki.documentfoundation.org/Macros/Python_Design_Guide)
* [PyUno documentation](http://www.openoffice.org/udk/python/python-bridge.html).
* [Apache OpenOffice Developer's Guide](https://wiki.openoffice.org/wiki/Documentation/DevGuide/OpenOffice.org_Developers_Guide)
* [Old StarOffice Programmer's Tutorial](https://www.openoffice.org/api/basic/man/tutorial/tutorial.pdf)
for main knowledge about OpenOffice UNO (Universal Network Objects) technology and how to use it.
* [LibreOffice SDK API documentation](https://api.libreoffice.org/docs/idl/ref/index.html).
* [Jamie Boyle’s Cookbook](https://documenthacker.files.wordpress.com/2013/07/writing_documents-_for_software_engineers_v0002.pdf).
* [Christopher Bourez's blog post](http://christopher5106.github.io/office/2015/12/06/openoffice-libreoffice-automate-your-office-tasks-with-python-macros.html)
* [Development enviroment setup using pyenv](https://gist.github.com/thekalinga/b74056272cb1afdabf529a332ff0f517).
* [LibreOffice's own Python examples](https://cgit.freedesktop.org/libreoffice/core/tree/pyuno/demo)
* [How to pack Python script as part of the document](https://wiki.openoffice.org/wiki/Python_as_a_macro_language)

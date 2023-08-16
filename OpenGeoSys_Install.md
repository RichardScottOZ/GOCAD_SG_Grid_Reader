## OpenGeoSys repo instructions

Rough and ready guide as a reminder to myself how I built ogs6-cli and ogs6-gui on Ubuntu 20.04
These are rough notes from memory representing a beginner’s strategy to finding a linux-friendly ogs6.

OS: Ubuntu 20.04
OGS gitlab repo: Tag v6.4.0

STRATEGY

This strategy means all the -deps are available for OGS-CLI and OGS-GUI
As a beginner, building OGS-GUI requires more consideration, so it is best to have OGS-CLI up and running first. The compilation of OGS-GUI is relatively quick if it is built inside existing OGS-CLI build

Install a decent build system (gcc etc)
see www.opengeosys.org/docs/devguide/getting-started/prerequisites/
Install python 3 (e.g. python 3.8 or python 3.9)
if you are using Python 3.9, build python3 package CoolProps - inside the CoolProps script dir: setup.py (up to now, pip3 install coolprops doesn’t work; tespy won’t install without it)
Then install tespy: pip3 install tespy

STEP-1: build OGS CLI with PYTHON=ON in dir ~/build/release
Leave CMakeList.txt unchanged
i.e. OGS_BUILD_GUI=OFF
git clone the tag release that you want

e.g. repo tag v6.4.0: git clone https://gitlab.opengeosys.org/ogs/ogs.git
Files · 6.4.0 · ogs / ogs · GitLab

git clone https://gitlab.opengeosys.org/ogs/ogs.git
(rename the source directory to ogs)
cd ogs
mkdir -p …/build/release
cd /build/release
cmake …/…/ogs -G Ninja -DCMAKE_BUILD_TYPE=Release
ninja -j 2

IMPT!! When CLI build OK, make a backup copy of the entire ogs source and build folders (e.g. ogs_640_CLI)

Comments:

Configure & Generate: cmake …/…/ogs -G Ninja -DCMAKE_BUILD_TYPE=Release
Build using ninja: ninja -j 2

If successful with configuring and generating, you will have this output in the terminal:

– The following features have been enabled:

OGS, The OGS simulator (OGS_BUILD_CLI)
Utilities, Command line tools (OGS_BUILD_UTILS)
Python-interface, Python boundary conditions and source terms (OGS_USE_PYTHON)
Tests, Unit and benchmarks tests (OGS_BUILD_TESTING)
build-unity, Unity build (OGS_USE_UNITY_BUILDS)
– Configuring done
– Generating done
– Build files have been written to: ~/ogs_640/build/release

If successful with the build, there will be no errors.

++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

STEP-2: build OGS-GUI in same dir for OGS-CLI: ~/build/release
These are the steps to build Data Explorer using the same ~/build/release folder as the OGS CLI version in STEP-1
IMPT!! When CLI build OK, make a backup copy of the entire ogs source and build folders (e.g. ogs_640_CLI)

For OGS-GUI v6.4.0:

(a) You need to install Qt v5.14.2 using aqtinstall, because in CMake-Gui, you will need to locate cmake Qt libraries in the Qt 5.14.2 dir to build Data Explorer.
pip3 install aqtinstall
mkdir /opt/qt
cd /opt/qt
aqt install-qt 5.14.2 linux desktop gcc_64 -m xmlpatterns,x11extras
You will probably have to change the last line (i.e. delete xmlpatterns,x11extras) if you get a syntax error. Note that ‘aqt install’ is deprecated.

(b) You need to build VTK v8.2 so that you can have several libraries e.g. vtkGuiSupportQt etc.
Use CMake-Gui for this and make sure vtkGuiSupprtQt is ticked! Otherwise these libraries wont be built!

In the ~/build/release dir in STEP-1, keep the original flags ON and set flag to build Data Explorer to on: OGS_BUILD_GUI ON and OGS_BUILD_CVODE ON
Open a terminal and open the CMake-Gui program
cmake-gui
Check source and build dirs
Check Generator is ninja
Press ‘Configure’

Now it is all red and you need to provide paths to Qt5 libraries
Set Qt dir to the Qt 5.14.2 cmake sub-directories
Set VTK dir to the compiled vtk-8.2 root folder, because this is where CMake will find the vtkGuiSupportQt libraries.

Check other flags are set (e.g. BUILD_GUI)
Press Configure (still red? fix errors)
Press Configure (nothing red? OK)
Press Generate

Close Cmake-Gui

In terminal: ninja -j 2

When build completed successfully, in same terminal: ./DataExplorer
When you first start Data Explorer, it will complain it is missing vtk libraries
Each time it starts, it will stop and in the termial the error states which library is missing.
You will find these in the vtk-8.2 folder. Copy and paste them into the ~build/release/lib folder (there will be several). Then ./DataExplorer will start

Read the Data Explorer manual.
Visit PyVista and PVGeo on Github
Look at the PVGeo repo for its winning geothermal entry (2nd place) on Utah FORGE Competition.

## Process Notes

Trying this out now, things I had to do, Ubuntu style

stackoverflow.com
user3871995
Ninja not found by CMake
cmake, ninja
asked by user3871995 on 11:45AM - 29 Jul 16 UTC
sudo apt-get install ninja-build

there was also a git version check error, so had to comment out
in scripts/cmake/GitSetup.cmake where it was checking the version

also looks like the certificate problem bites too

```C++
[1/9] Creating directories for ‘xmlpatch-populate’
[2/9] Performing download step (git clone) for ‘xmlpatch-populate’
Cloning into ‘xmlpatch-src’…
fatal: unable to access ‘https://gitlab.opengeosys.org/ogs/libs/xmlpatch.git/’: server certificate verification failed. CAfile: /etc/ssl/certs/ca-certificates.crt CRLfile: none
Failed to clone repository:

string(REPLACE “.windows.1” “” GIT_VERSION_STRING GITVERSIONSTRING)
if
(
 {GIT_VERSION_STRING} VERSION_LESS 
 ogs.minimumversion.git)
 message(FATALERROR"Gitversion
 {ogs.minimum_version.git} is required.
Found version ${GIT_VERSION_STRING}."
)
endif()
```

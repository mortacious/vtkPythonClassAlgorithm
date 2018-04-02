# cmake -G Ninja -DCMAKE_BUILD_TYPE=Debug -DParaView_DIR:PATH=$PWD/../../ParaView-build-py3/ -DQt5_DIR:PATH=/opt/Qt-5.9.1/5.9.1/clang_64/lib/cmake/Qt5/ ..
# old: cmake -G Ninja -DCMAKE_BUILD_TYPE=Debug -DVTK_DIR:PATH=/Users/bob.pepin/Documents/Paraview/ParaView-build/VTK -DParaView_DIR:PATH=$PWD/../../ParaView-build/ -DQt5_DIR:PATH=/opt/Qt-5.7.1/5.7/clang_64/lib/cmake/Qt5/ ..

cmake_minimum_required(VERSION 3.8)
 
PROJECT(PythonClassAlgorithm)

find_package(ParaView REQUIRED)
include(${ParaView_USE_FILE})
#find_package(VTK REQUIRED)
#include(${VTK_USE_FILE})

find_package(Boost REQUIRED COMPONENTS system filesystem)
#link_directories(/Applications/paraview.app/Contents/Libraries/)
#add_executable(PythonClassAlgorithm MACOSX_BUNDLE PythonClass
# vtkPythonClassAlgorithm)

include(ParaViewPlugins)

ADD_PARAVIEW_PLUGIN(SMPythonClassAlgorithm "1.0"
  SERVER_MANAGER_XML PythonClassAlgorithm.xml
  SERVER_MANAGER_SOURCES src/vtkPythonClassAlgorithm.cxx include/vtkPythonClassAlgorithm.h include/file_changed_monitor.h src/file_changed_monitor.cpp)
target_link_libraries(SMPythonClassAlgorithm LINK_PUBLIC ${VTK_LIBRARIES})

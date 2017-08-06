# cmake -DVTK_DIR:PATH=/Users/bob.pepin/Documents/Paraview/ParaView-build/VTK -DParaView_DIR:PATH=$PWD/../../ParaView-build/ -DQt5_DIR:PATH=/opt/Qt-5.7.1/5.7/clang_64/lib/cmake/Qt5/ ..

cmake_minimum_required(VERSION 3.8)
 
PROJECT(PythonClassAlgorithm)

find_package(ParaView REQUIRED)
include(${ParaView_USE_FILE})
find_package(VTK REQUIRED)
include(${VTK_USE_FILE})
	
#link_directories(/Applications/paraview.app/Contents/Libraries/)
#add_executable(PythonClassAlgorithm MACOSX_BUNDLE PythonClass
# vtkPythonClassAlgorithm)

include(ParaViewPlugins)

set(PCA_BUILD_MAIN 0)
# create a paraview plugin containing server manager xml and the server
# manager classes to build
# this plugin can be loaded on the server side
if(PCA_BUILD_MAIN)

add_executable(PythonClassAlgorithm PythonClass vtkPythonClassAlgorithm)	
target_link_libraries(PythonClassAlgorithm ${VTK_LIBRARIES})

else(PCA_BUILD_MAIN)

ADD_PARAVIEW_PLUGIN(SMPythonClassAlgorithm "1.0"
  SERVER_MANAGER_XML PythonClassAlgorithm.xml
  SERVER_MANAGER_SOURCES vtkPythonClassAlgorithm.cxx)
target_link_libraries(SMPythonClassAlgorithm LINK_PUBLIC ${VTK_LIBRARIES})

endif(PCA_BUILD_MAIN)

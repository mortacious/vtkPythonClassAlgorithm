//
// Created by mortacious on 4/2/18.
//

#pragma once
#ifndef VTKPYTHONCLASSALGORITHM_UTILS_H
#define VTKPYTHONCLASSALGORITHM_UTILS_H

#include <boost/filesystem/operations.hpp>
#include <ctime>
namespace util {
    class FileChangedMonitor {
    public:
        FileChangedMonitor(const boost::filesystem::path& p);
        FileChangedMonitor(const std::string& path);


        bool check_modified();
    private:
        std::time_t last_modified();
        boost::filesystem::path _file;
        std::time_t _last_written;
    };
}
#endif //VTKPYTHONCLASSALGORITHM_UTILS_H

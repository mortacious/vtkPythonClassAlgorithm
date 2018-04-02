//
// Created by mortacious on 4/2/18.
//

#include <file_changed_monitor.h>
using namespace util;

FileChangedMonitor::FileChangedMonitor(const boost::filesystem::path& p): _file(p) {
    _last_written = last_modified();
}

FileChangedMonitor::FileChangedMonitor(const std::string& path): FileChangeMonitor(boost::filesystem::path(path)) {}

bool FileChangedMonitor::check_modified() {
    std::time_t t = boost::filesystem::last_write_time(_file);
    if(t > _last_written) {
        _last_written = t;
        return true;
    }
    return false;
}

std::time_t last_modified() {
    return boost::filesystem::last_write_time(_file);
}



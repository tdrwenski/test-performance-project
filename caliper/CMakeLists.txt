cmake_minimum_required(VERSION 3.10)
project(SimpleBenchmark)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(PkgConfig REQUIRED)
pkg_check_modules(CALIPER REQUIRED caliper)

add_executable(simple_benchmark simple_benchmark.cpp)
target_link_directories(simple_benchmark PRIVATE ${CALIPER_LIBRARY_DIRS})
target_link_libraries(simple_benchmark ${CALIPER_LIBRARIES})
target_include_directories(simple_benchmark PRIVATE ${CALIPER_INCLUDE_DIRS})
target_compile_options(simple_benchmark PRIVATE ${CALIPER_CFLAGS_OTHER})

# Set rpath for macOS
if(APPLE)
    set_target_properties(simple_benchmark PROPERTIES
        INSTALL_RPATH "${CALIPER_LIBRARY_DIRS}"
        BUILD_WITH_INSTALL_RPATH TRUE
    )
endif()
cmake_minimum_required(VERSION 3.10)
project(caliper-benchmark)

find_package(caliper)
add_executable(simple_benchmark simple_benchmark.cpp)
target_link_libraries(simple_benchmark PRIVATE caliper)
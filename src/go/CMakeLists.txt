cmake_minimum_required(VERSION 3.16)
project(go C)

set(CMAKE_C_STANDARD 11)

add_library(go library.h color.h color.c constants.h coordinate.c coordinate.h)
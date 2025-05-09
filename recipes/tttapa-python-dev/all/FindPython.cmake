set(_find_python_args_fwd)
if (${CMAKE_FIND_PACKAGE_NAME}_FIND_VERSION)
    list(APPEND _find_python_args_fwd ${${CMAKE_FIND_PACKAGE_NAME}_FIND_VERSION})
endif()
if (${CMAKE_FIND_PACKAGE_NAME}_FIND_VERSION_EXACT)
    list(APPEND _find_python_args_fwd EXACT)
endif()
if (${CMAKE_FIND_PACKAGE_NAME}_FIND_QUIETLY)
    list(APPEND _find_python_args_fwd QUIET)
endif()
list(APPEND _find_python_args_fwd MODULE)
if (${CMAKE_FIND_PACKAGE_NAME}_FIND_REQUIRED)
    list(APPEND _find_python_args_fwd REQUIRED)
endif()
set(_find_python_components)
set(_find_python_optional_components)
foreach(c IN LISTS ${CMAKE_FIND_PACKAGE_NAME}_FIND_COMPONENTS)
    if (${CMAKE_FIND_PACKAGE_NAME}_FIND_REQUIRED_${c})
        list(APPEND _find_python_components ${c})
    else()
        list(APPEND _find_python_optional_components ${c})
    endif()
endforeach()
if (_find_python_components)
    list(APPEND _find_python_args_fwd COMPONENTS ${_find_python_components})
endif()
if (_find_python_optional_components)
    list(APPEND _find_python_args_fwd OPTIONAL_COMPONENTS ${_find_python_optional_components})
endif()

@FIND_PYTHON_HINTS@

set(_find_python_cmake_module_path_restore ${CMAKE_MODULE_PATH})
list(REMOVE_ITEM CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
list(JOIN _find_python_args_fwd " " _find_python_args_fwd_str)
message(STATUS "Conan tttapa-python-dev: find_package(${CMAKE_FIND_PACKAGE_NAME} ${_find_python_args_fwd_str})")
find_package(${CMAKE_FIND_PACKAGE_NAME} ${_find_python_args_fwd})
set(CMAKE_MODULE_PATH ${_find_python_cmake_module_path_restore})

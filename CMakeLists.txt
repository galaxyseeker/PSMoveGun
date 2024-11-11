cmake_minimum_required(VERSION 3.15)
set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)

project(PSMoveGun)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# 启用更详细的构建输出
set(CMAKE_VERBOSE_MAKEFILE ON)

# 设置 Eigen 包含路径
set(EIGEN3_INCLUDE_DIR ${CMAKE_CURRENT_SOURCE_DIR}/vcpkg/installed/x64-windows/include)

# 查找 Eigen 包
find_package(Eigen3 CONFIG REQUIRED)

# 添加源文件
add_library(psmove_gun SHARED
    psmove_data_fetcher.cpp
    psmove_core/ServerControllerView.cpp
    psmove_core/ServerDeviceView.cpp
    psmove_core/PSMoveControllerDeviceInterface.cpp
    psmove_core/DeviceManager.cpp
    psmove_core/LoggerUtil.cpp
)

# 链接 Eigen 并设置包含目录
target_link_libraries(psmove_gun PRIVATE Eigen3::Eigen)
target_include_directories(psmove_gun PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}/psmove_core
    ${EIGEN3_INCLUDE_DIR}
)

# 设置输出目录
set_target_properties(psmove_gun PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin"
    LIBRARY_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin"
    ARCHIVE_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin"
    PREFIX ""
)

# 确保生成 .lib 文件
if(MSVC)
    set_target_properties(psmove_gun PROPERTIES
        IMPORT_SUFFIX ".lib"
    )
endif()

# 添加可执行文件
add_executable(test_psmove_gun test_psmove_gun.cpp)
target_link_libraries(test_psmove_gun PRIVATE psmove_gun)

# 确保测试可执行文件能找到 psmove_gun.dll
set_target_properties(test_psmove_gun PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin"
)

# 复制 DLL 到测试可执行文件目录
add_custom_command(TARGET test_psmove_gun POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy_if_different
        "${CMAKE_BINARY_DIR}/bin/$<CONFIG>/psmove_gun.dll"
        $<TARGET_FILE_DIR:test_psmove_gun>
)

# 添加调试输出
message(STATUS "RUNTIME_OUTPUT_DIRECTORY: ${CMAKE_RUNTIME_OUTPUT_DIRECTORY}")
message(STATUS "LIBRARY_OUTPUT_DIRECTORY: ${CMAKE_LIBRARY_OUTPUT_DIRECTORY}")
message(STATUS "ARCHIVE_OUTPUT_DIRECTORY: ${CMAKE_ARCHIVE_OUTPUT_DIRECTORY}")
message(STATUS "psmove_gun library file: $<TARGET_LINKER_FILE:psmove_gun>")

# 添加自定义命令来检查文件是否存在
add_custom_command(TARGET psmove_gun POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E echo "psmove_gun build completed"
)

set(CMAKE_TOOLCHAIN_FILE "${CMAKE_CURRENT_SOURCE_DIR}/vcpkg/scripts/buildsystems/vcpkg.cmake" CACHE STRING "Vcpkg toolchain file")

add_definitions(-DEIGEN_MPL2_ONLY)
add_definitions(-DEIGEN_MAX_CPP_VER=17)  # 如果你使用 C++17

if(MSVC)
    add_compile_options(/EHsc /bigobj)
endif()

# 现有的代码...

# 添加以下行来查找 Eigen 包
find_package(Eigen3 REQUIRED)

# 在您的目标设置中添加 Eigen 的包含目录
target_include_directories(psmove_gun PRIVATE ${EIGEN3_INCLUDE_DIR})
target_include_directories(test_psmove_gun PRIVATE ${EIGEN3_INCLUDE_DIR})

# 如果您有其他目标也需要使用 Eigen，也为它们添加包含目录

# 现有的代码...

# 添加以下调试输出
message(STATUS "CMAKE_BINARY_DIR: ${CMAKE_BINARY_DIR}")
message(STATUS "psmove_gun library file: $<TARGET_LINKER_FILE:psmove_gun>")
message(STATUS "psmove_gun import library: $<TARGET_LINKER_FILE_NAME:psmove_gun>")

# 确保 test_psmove_gun 在 psmove_gun 之后构建
add_dependencies(test_psmove_gun psmove_gun)

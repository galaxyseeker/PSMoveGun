# PSMoveGun Project

这是一个基于Github上的PSMoveService 的 C++ 库，用于与 PS Move 控制器交互。

## 依赖

- CMake 3.15+
- vcpkg
- Eigen3

## 构建说明

1. 安装 vcpkg：   ```
   git clone https://github.com/Microsoft/vcpkg.git
   cd vcpkg
   .\bootstrap-vcpkg.bat   ```

2. 安装 Eigen：   ```
   .\vcpkg install eigen3:x64-windows   ```

3. 配置项目：   ```
   "C:\Program Files\CMake\bin\cmake.exe" -B build -S . -DCMAKE_TOOLCHAIN_FILE=[path to vcpkg]/scripts/buildsystems/vcpkg.cmake   ```

4. 构建项目：   ```
   "C:\Program Files\CMake\bin\cmake.exe" --build build --config Release   ```

## 使用说明

1. 包含头文件：   ```cpp
   #include "psmove_data_fetcher.h"   ```

2. 创建和使用 PSMoveDataFetcher：   ```cpp
   PSMoveDataFetcher* fetcher = create_fetcher();
   if (initialize_fetcher(fetcher)) {
       CommonDevicePose pose = get_pose_data(fetcher);
       // 使用 pose 数据...
   }
   destroy_fetcher(fetcher);   ```

## 注意事项

- 确保 PS Move 控制器已连接并被系统识别。
- 这个库目前只支持 Windows 平台。

## 贡献

欢迎提交 issues 和 pull requests。

## 许可

[在这里添加你的许可信息]

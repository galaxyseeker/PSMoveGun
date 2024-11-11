@echo off
echo Cleaning build directory...
if exist build rmdir /s /q build
mkdir build

echo Running CMake configure...
"C:\Program Files\CMake\bin\cmake.exe" -B build -S . -DCMAKE_TOOLCHAIN_FILE=C:/Users/galax/Desktop/PSMoveGun/Programs/PSMoveGunProj/vcpkg/scripts/buildsystems/vcpkg.cmake
if %ERRORLEVEL% neq 0 (
    echo CMake configure failed with error code %ERRORLEVEL%
    exit /b %ERRORLEVEL%
)

echo Running CMake build...
"C:\Program Files\CMake\bin\cmake.exe" --build build --config Release --verbose
if %ERRORLEVEL% neq 0 (
    echo CMake build failed with error code %ERRORLEVEL%
    exit /b %ERRORLEVEL%
)

echo Build completed successfully

echo Checking for generated files...
if exist build\bin\Release\psmove_gun.dll (
    echo psmove_gun.dll found
) else (
    echo psmove_gun.dll not found
)

if exist build\bin\Release\psmove_gun.lib (
    echo psmove_gun.lib found
) else (
    echo psmove_gun.lib not found
)

if exist build\bin\Release\test_psmove_gun.exe (
    echo test_psmove_gun.exe found
) else (
    echo test_psmove_gun.exe not found
)

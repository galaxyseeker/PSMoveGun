注意：此文档每天维护。

置顶：
现在借鉴这些代码，实现我们的鼠标控制功能。也就是我要使用psmovecontroller在空间中的姿态，利用它的指向，在PC，windows11环境下的屏幕上移动鼠标或者改变鼠标的位置。请你综合考虑是否还有其它影响的参数需要提供。

算法：
控制鼠标的原理：在Move Controller的轴线向灯球前方的延长线到达屏幕以后的交点，就是鼠标的位置。屏幕的平面是一个虚拟的面，一开始不做矫正，假设为距离Controller原始轴线延长线前方0.5米的地方。



2024年10月29日 10点30分 ****************************************************

1.DeviceManager在ServerControllerView.cpp中被调用，所以我的文件也需要实现这些功能。
        设备的生命周期管理（启动、更新、关闭）
        设备的热插拔检测和处理
        设备状态的轮询和更新
        设备数据的发布给客户端
    现在的问题是原始类是在ServerControllerView.cpp中实现，但是我这一部分逻辑被放到了psmove_data_fetcher.cpp中。

2.PSMoveService.cpp文件，实现了整个PSMoveService的启动和关闭。它调用了多个Manager的startup()方法，其中也包括DeviceManager的startup()方法，从而实现初始化。

3.C:\Users\galax\Desktop\PSMoveGun\Programs\PSMoveService\src\psmoveservice\Server\EntryPoint.cpp是程序的入口点：
        //-- includes -----
        #include "PSMoveService.h"

        //-- entry point -----
        int main(int argc, char *argv[])
        {
            PSMoveService app;

            return app.exec(argc, argv);
        }

4. C:\Users\galax\AppData\Roaming\PSMoveService目录下面保存了所有的校准文件。



2024年10月28日 18点13分 ****************************************************

重新和网页版Claude讨论了技术细节，我的ServerControllerView类，需要实现以下功能：（但是我还要验证一下是不是需要这些功能）

//////////////////ServerControllerView.cpp//////////////////开始
分析你的实现版本，还需要添加以下关键组件：

1. 数据队列系统：（暂时在本地处理数据，不需要）
```cpp
// 添加数据队列用于IMU和光学数据
private:
    // 可以使用std::queue或自定义无锁队列
    std::queue<IMUData> m_imu_data_queue;
    std::queue<OpticalData> m_optical_data_queue;
```

2. 追踪状态管理：（部分实现，实现LED控制）
```cpp
private:
    // 追踪状态相关
    bool m_tracking_enabled;
    int m_tracking_listener_count;
    
    // LED控制相关
    struct LEDState {
        uint8_t r, g, b;
        bool override_active;
    } m_led_state;
```

3. 设备状态和连接管理：（设备状态需要实现，没有DeviceConfig,这是AI的错误）
实现DeviceManager::startup()，
```cpp
private:
    // 设备状态
    bool m_is_connected;
    bool m_is_bluetooth;
    std::string m_device_serial;
    
    // 连接配置
    struct DeviceConfig {
        std::string bluetooth_addr;
        std::string usb_path;
    } m_config;
```

4. 姿态滤波器接口：(需要实现)
```cpp
class IPoseFilter {
public:
    virtual void reset() = 0;
    virtual void update(const IMUData& imu_data) = 0;
    virtual CommonDevicePose getPose(float prediction_time) const = 0;
    virtual ~IPoseFilter() = default;
};

private:
    std::unique_ptr<IPoseFilter> m_pose_filter;
```

5. 光学追踪系统扩展：（暂时不需要）
```cpp
struct OpticalPoseEstimation {
    bool is_tracking;
    std::chrono::time_point<std::chrono::high_resolution_clock> last_visible_time;
    CommonDevicePose pose;
    
    void clear() {
        is_tracking = false;
        pose = CommonDevicePose();
    }
};

private:
    std::vector<OpticalPoseEstimation> m_tracker_pose_estimations;
```

6. 公共接口方法：（需要实现）
```cpp
public:
    // 追踪控制
    void startTracking();
    void stopTracking();
    
    // LED控制
    void setLEDColor(uint8_t r, uint8_t g, uint8_t b);
    void clearLEDOverride();
    
    // 设备状态查询
    bool isConnected() const;
    bool isBluetooth() const;
    std::string getSerial() const;
    
    // 姿态重置和校准
    void resetOrientation();
    void calibratePosition();
```

7. 事件通知系统：（需要实现，在DeviceInterface.h文件中实现）
```cpp
public:
    // 事件回调接口
    class IControllerListener {
    public:
        virtual void onControllerConnected() = 0;
        virtual void onControllerDisconnected() = 0;
        virtual void onButtonPressed(int button_id) = 0;
        virtual void onButtonReleased(int button_id) = 0;
        virtual void onPoseUpdated(const CommonDevicePose& pose) = 0;
        virtual ~IControllerListener() = default;
    };
    
    void addListener(IControllerListener* listener);
    void removeListener(IControllerListener* listener);
    
private:
    std::vector<IControllerListener*> m_listeners;
```

8. 错误处理和诊断：(源代码中没有，不需要)
```cpp
class ControllerError : public std::runtime_error {
public:
    explicit ControllerError(const std::string& msg) : std::runtime_error(msg) {}
};

private:
    // 错误状态
    std::string m_last_error;
    int m_error_count;
    
public:
    std::string getLastError() const;
    void clearError();
```

9. 配置管理：（需要实现）
```cpp
struct ControllerConfig {
    float prediction_time;
    float tracking_sensitivity;
    bool use_accelerometer;
    bool use_gyroscope;
    // ... 其他配置项
};

private:
    ControllerConfig m_config;
public:
    void setConfig(const ControllerConfig& config);
    ControllerConfig getConfig() const;
```

建议实现顺序：
1. 首先实现基础的设备接口和状态管理
2. 添加姿态滤波器系统
3. 实现光学追踪支持
4. 添加数据队列管理
5. 实现事件通知系统
6. 添加配置和错误处理

//////////////////ServerDeviceView.cpp//////////////////结束







2024年10月23日 17：06 ****************************************************

又搞了几乎一天编译的链接静态文件的问题，想在初步的正确版本有了，可以生成可执行文件。现在上传到Github进行版本管理。




2024年10月22日 09:27 ****************************************************

今天开始编译代码，添加实际的逻辑。昨天已经把整个项目转换为纯c++的项目这样看起来会顺很多。

Cmake上面花费了一些时间，新版本的安装会删除旧版本,所以现在的新版本是3.31而并不是以前需要的3.6.1

花了几乎一天的时间在编译原始版本的可执行文件和动态及静态库上面，现在终于成功了。





2024年10月21日 11：10 ****************************************************

又研究了三天，还是没有解决取得姿态数据的问题。

把ServerControllerView类的作用重新列了一下，放到这里。

以下是 PSMoveService 库中 ServerControllerView 的工作原理说明：

//////////////////ServerControllerView.cpp//////////////////
初始化和设备管理：
ServerControllerView 类继承自 ServerDeviceView，用于管理单个 PS Move 控制器。
在构造函数中，它初始化控制器的基本属性，如设备ID、跟踪状态和姿态过滤器。
设备打开和配置：
open() 方法用于打开和初始化控制器设备。
它会分配设备接口，设置跟踪颜色，并初始化姿态过滤器。
如果控制器是通过蓝牙连接的，还会进行额外的配置。
姿态过滤和跟踪：
resetPoseFilter() 方法根据控制器类型（如 PSMove 或 DualShock4）初始化适当的姿态过滤器。
getFilteredPose() 方法返回经过过滤的控制器姿态数据，包括位置和方向。
光学跟踪更新：
updateOpticalPoseEstimation() 方法使用摄像头数据更新控制器的光学姿态估计。
它处理单摄像头和多摄像头的情况，计算控制器的 3D 位置。
数据流处理：
notifySensorDataReceived() 方法处理从控制器接收到的新传感器数据。
它更新内部状态并准备数据以供进一步处理。
状态更新和预测：
updateStateAndPredict() 方法整合来自不同来源的数据（如 IMU 和光学跟踪），更新控制器状态并进行预测。
数据发布：
publish_device_data_frame() 方法准备并发送控制器数据帧到客户端。
根据控制器类型（PSMove、PSNavi、DualShock4等），生成相应格式的数据帧。
辅助功能：
提供了各种辅助方法，如设置 LED 颜色、启用/禁用跟踪、获取电池状态等。
多摄像头支持：
实现了从多个摄像头数据中计算控制器位置的方法，提高跟踪精度。
错误处理和日志：
包含了错误检查和日志记录，以便于调试和监控系统状态。
这个组件是 PSMoveService 的核心，它将硬件接口、数据处理和状态管理整合在一起，为上层应用提供了一个统一的控制器视图。它的设计允许灵活处理不同类型的控制器，并能够适应不同的跟踪环境（单摄像头或多摄像头）。
//////////////////ServerDeviceView.cpp//////////////////
这个文件是 PSMoveService 库中设备视图的基类实现，为所有具体设备视图（如 ServerControllerView）提供了通用功能。以下是其主要功能和工作原理的说明：
初始化和构造：
ServerDeviceView 构造函数初始化基本属性，如设备ID、轮询计数器和序列号。
它为所有设备视图提供了一个通用的初始化过程。
设备打开和关闭：
open() 方法是一个虚函数，用于打开设备。它调用子类实现的 allocate_device_interface() 方法来分配具体的设备接口。
close() 方法关闭设备，释放资源，并调用 free_device_interface() 来清理设备特定的接口。
数据轮询和更新：
poll() 方法定期检查设备的新数据。它管理轮询计数和序列号，以跟踪数据更新。
如果检测到新数据，它会标记状态为未发布，准备后续处理。
数据发布：
publish() 方法负责发布设备的最新数据。它调用子类实现的 publish_device_data_frame() 方法来处理具体的数据发布逻辑。
设备匹配：
matchesDeviceEnumerator() 方法用于检查当前设备是否匹配给定的设备枚举器，这在设备识别和管理中很有用。
状态管理：
getIsOpen() 检查设备是否已打开。
getHasUnpublishedState() 和 markStateAsUnpublished() 用于管理数据的发布状态。
getLastNewDataTimestamp() 返回最后一次接收新数据的时间戳。
7. 设备接口管理：
allocate_device_interface() 和 free_device_interface() 是纯虚函数，由子类实现，用于管理具体设备的接口。
数据帧发布：
publish_device_data_frame() 也是一个纯虚函数，由子类实现具体的数据发布逻辑。
错误处理和日志：
包含了基本的错误检查和日志记录，以便于调试和监控。
ServerDeviceView.cpp 的主要作用是提供一个通用的框架，用于管理各种类型的设备（如控制器、追踪器等）。它处理了设备生命周期管理、数据轮询和发布的通用逻辑，同时通过虚函数允许子类（如 ServerControllerView）实现特定设备的具体行为。
这种设计促进了代码重用，并为不同类型的设备提供了一致的接口，使得 PSMoveService 能够统一管理多种设备，同时保持了足够的灵活性来处理每种设备的特殊需求。



正在解决以下问题：
创建 ConcretePoseFilter 类，它应该继承自 IPoseFilter。
创建 ConcreteDeviceInterface 类，它应该继承自 IDeviceInterface。
在 DeviceInterface.h 中定义 CommonControllerState、CommonDevicePose 等结构。
实现 TrackerManager 类及其相关方法。


16：30分 终于解决了controller框架迁移搭建的问题。又用了一天时间，但是具体的方法逻辑还需要完善。



2024年10月17日 11：40 ****************************************************

终于把引用的PSMoveService库里的所有问题错误都解决了。大部分是因为路径设置的问题。记得用**包含子目录的所有路径。

c_cpp_properties.json文件的include path路径设置如下：
                "${workspaceFolder}/**",
                "C:\\Users\\galax\\Desktop\\PSMoveGun\\Programs\\PSMoveService\\src\\psmoveservice\\**",
                "C:\\Users\\galax\\Desktop\\PSMoveGun\\Programs\\PSMoveService\\src\\psmovemath",
                "C:\\Users\\galax\\Desktop\\PSMoveGun\\Programs\\PSMoveService\\src\\psmoveprotocol",
                "C:\\Users\\galax\\Desktop\\PSMoveGun\\Programs\\PSMoveService\\thirdparty\\**",
                "C:\\Users\\galax\\Desktop\\PSMoveGun\\Programs\\PSMoveService\\build\\src\\psmoveprotocol",
                "C:\\local\\boost_1_61_0\\**"

现在终于可以尝试使用直接获取姿态的方法来实现鼠标的移动。




2024年10月12日 10点06分 ****************************************************

停止股市交易佣金计算器的开发。把宝贵的时间用到最重要的开发上面，要实现的想法太多了。

很多股市的人和软件都说“据此操作，后果自负”，我觉得好多人就是没有根据前人的经验来操作，才导致亏损的后果。

就是应该给出操作建议。

而且很多人都是犯的低级错误。这个时候应该给出这样操作导致后果的提示，并给出这样操作的出处。出自某一本书，或者某一篇文章。




2024年10月11日 11点12分 ****************************************************

昨天晚上遇到交易佣金计算的问题，今天顺手做了个交易佣金计算器。
路径：C:\Users\galax\Desktop\PSMoveGun\Programs\SaveYourTxnFee.py
可执行文件在C:\Users\galax\Desktop\PSMoveGun\Programs\PSMoveGunProj\dist\SaveYourTxnFee.exe

Python这个语言不能运行在网页上，但是可以编译成exe文件。运行在网页上可以改成Javascript。


又用了半天时间改进了交易佣金计算器。在强大的Python的帮助下增加了以下功能：
1. 增加了公式显示。
2. 增加了费用占比显示。
3. 增加了交易总额显示。
4. 按钮图片化
5. 播放音效，语音朗读计算结果
6. 日志功能，日志表格化


启发：另外想到一些问题，所有赚钱的工具都在Apple手机上，所以应该将所有的应用都至少做一个App store版本。Claude给了我一些提示，都比较有用。
不过计算器的应用实在太多了，这不是一个很好的选择。


另外测试了界面背景图片随机显示的功能。
--------------------------------    

现在仍然回到PSMoveService，解决鼠标指针漂移的问题。

终于找到了在ServerControllerView.cpp文件里获取姿态的逻辑。
函数static void generate_psmove_data_frame_for_stream中，
    const CommonDevicePose controller_pose = controller_view->getFilteredPose(psmove_config->prediction_time); 
最重要的就是这个数据，只要取到了，就完事了。可以直接使用。这里的代码过渡封装了，不用研究了。


调用关系：
C:\Users\galax\Desktop\PSMoveGun\Programs\PSMoveService\src\psmoveservice\Server\ServerRequestHandler.cpp里面会调用：
    // -- Controller Requests -----
    inline ServerControllerView *get_controller_view_or_null(int controller_id)
待续。。。。。


Controller Manager类里面

ServerControllerViewPtr
ControllerManager::getControllerViewPtr(int device_id)
{
    assert(m_deviceViews != nullptr);

    return std::static_pointer_cast<ServerControllerView>(m_deviceViews[device_id]);
}
会构造ServerControllerView对象

        void ServerControllerView::generate_controller_data_frame_for_stream
            调用
            static void generate_psmove_data_frame_for_stream
                        获取姿态
                        controller_view->getFilteredPose(psmove_config->prediction_time);
--------------------------------







2024年10月10日 ****************************************************

今天开始利用Cursor的AI工具来编写代码。但是程序改为使用C++实现，以解决按键检测的问题。以前的代码更新至C:\Users\galax\Desktop\PSMoveGun\Programs\PSMoveGunProj\psmove_mouse_controller1.5.py截至。
这个版本的python程序，可以正常运行，但是有按键检测的问题。另外鼠标的指针稳定性不够，还有些漂移。移动出屏幕然后再回到屏幕内的时候，指针会并不会回到控制器的指向位置。

新版本的C++程序，主要解决以下几个问题：
1. 按键检测的问题。
2. 鼠标指针漂移的问题。
3. 鼠标指针移动到屏幕外再回到屏幕内的时候，指针不会回到控制器的指向位置。

我觉得控制器指针的问题，应该有很多成熟的方案。但是目前AI没有给我提供任何有用的信息。

注意Include path的设置问题，现在还不是很明白这个设置在哪个层面起作用。

注意：修改了原始PSMoveService的代码，把SharedConstants.h文件拷贝到psmoveclient目录下。

一下子觉得茫无头绪。又调转回头Python代码。

以下是Python代码的最新进展：

1. 修正了鼠标指针漂移的问题。
2. 增加了日志输出类。文件名：psmove_logger_util.py



2024年10月9日 ****************************************************

开始使用Cursor开发，这个工具很强大，但是很多巨大的Bug。比如回退可以直接把创建的文件都删除掉。或者拷贝粘贴进了不相干的东西。



2024年10月8日 ****************************************************

解决检测按键的问题。没有太大进展。




2024年10月7日 ****************************************************

继续解决参数值为零的问题。

现在开始借鉴操作鼠标的算法：
C:\Users\galax\Desktop\PSMoveGun\Programs\PSMoveService\src\psmoveconfigtool\AppStage_MagnetometerCalibration.cpp 里面设置或者控制了Controller的姿态，通过查找关键字“Hold the Select button with controller pointed forward”
可以找到相应的代码。

所有问题都解决了，今天最重要的一点就是要把算法给AI讲明白否则它无法实现我想要的功能。
明天继续优化代码实现鼠标刷新率的提高，现在鼠标的反应仍然很慢。代码的刷新帧率只有8，希望明天直接调用windows的api函数将它的刷新率提高。


2024年10月6日 ****************************************************

结果需要运行服务器端，获取姿态数据的程序（客户端）才能运行。

C:\Users\galax\Desktop\PSMoveGun\Programs\PSMoveService\src\psmoveclient\PSMoveClient_CAPI.cpp里面的函数：
PSMResult PSM_GetControllerList(PSMControllerList *out_controller_list, int timeout_ms)
{
	PSMBlockingRequest request(g_psm_client->get_controller_list());
    PSMResult result_code= request.send(timeout_ms);

    if (g_psm_client != nullptr && result_code == PSMResult_Success)
    {
        assert(request.get_response_payload_type() == PSMResponseMessage::_responsePayloadType_ControllerList);
        
        *out_controller_list= request.get_response_message().payload.controller_list;
        result_code= PSMResult_Success;
    }
    
    return result_code;
}
是第一个关键点。

现在的问题是无法取到姿态的参数值。


2024年10月5日 ****************************************************
重新开一个AI对话。

AppStage_ControllerSettings.cpp这个类实现了test orientation的功能。
AppStage_MagnetometerCalibration.cpp这个类实现了具体的功能。
根据提供的代码,Test Orientation功能主要在AppStage_MagnetometerCalibration类中实现。以下是关键部分:

1. 在enter()函数中,它设置了相机和控制器视图。

2. update()函数处理不同的校准阶段,包括:
   - 测量磁力计范围
   - 等待重力对齐
   - 测量磁场方向
   - 设置校准

3. render()函数负责渲染3D视图,显示控制器模型、磁力计数据点云等。

4. renderUI()函数处理用户界面,包括进度条和说明文本。

5. 在complete状态下,它显示控制器的姿态、航向和倾斜角:

```cpp
PSMQuatf orientation;            
if (PSM_GetControllerOrientation(m_controllerView->ControllerID, &orientation) == PSMResult_Success)
{
    const Eigen::Quaternionf eigen_quat = psm_quatf_to_eigen_quaternionf(orientation);
    const Eigen::EulerAnglesf euler_angles = eigen_quaternionf_to_euler_angles(eigen_quat);

    ImGui::Text("Attitude: %.2f, Heading: %.2f, Bank: %.2f",
        euler_angles.get_attitude_degrees(), euler_angles.get_heading_degrees(), euler_angles.get_bank_degrees());
}
```

6. 它还提供了重置控制器中心的说明:

```cpp
ImGui::TextWrapped(
    "[Hold the Select button with controller pointed forward\n" \
    "to recenter the controller]");
```

这个类实现了完整的磁力计校准过程,并在校准完成后提供了测试方向的功能。图片中显示的界面对应于complete状态下的renderUI()部分。
#######################################

根据您提供的代码，AppStage_GyroscopeCalibration 类实现了陀螺仪校准和测试功能。以下是关键部分的分析：

1. 校准过程：
   - 等待控制器稳定
   - 测量陀螺仪的偏差和漂移
   - 计算校准参数并发送到服务器

2. 测试功能（eCalibrationMenuState::test 状态）：
   - 显示控制器的实时方向数据
   - 显示陀螺仪的校准后数据
   - 提供重置控制器方向的说明

3. 关键代码段（在 renderUI 函数的 test 状态下）：

```cpp
PSMQuatf controllerQuat;
if (PSM_GetControllerOrientation(m_controllerView->ControllerID, &controllerQuat) == PSMResult_Success)
{
    const Eigen::Quaternionf eigen_quat = psm_quatf_to_eigen_quaternionf(controllerQuat);
    const Eigen::EulerAnglesf euler_angles = eigen_quaternionf_to_euler_angles(eigen_quat);

    ImGui::Text("Pitch(x): %.2f, Yaw(y): %.2f, Roll(z): %.2f",
        m_lastCalibratedGyroscope.x * k_radians_to_degreees, 
        m_lastCalibratedGyroscope.y * k_radians_to_degreees,
        m_lastCalibratedGyroscope.z * k_radians_to_degreees);
    ImGui::Text("Attitude: %.2f, Heading: %.2f, Bank: %.2f", 
        euler_angles.get_attitude_degrees(), euler_angles.get_heading_degrees(), euler_angles.get_bank_degrees());
}
```

这段代码获取控制器的方向，并显示陀螺仪数据（pitch, yaw, roll）和欧拉角（attitude, heading, bank）。

4. 重置控制器方向的说明：
   - 对于 DualShock4 控制器：按 Options 按钮
   - 对于 PSMove 控制器：按住 Select 按钮

5. 3D 渲染：
   在 render 函数的 test 状态下，代码使用 OpenGL 绘制了控制器模型和坐标轴，展示了控制器的实时方向。

总结：这个类提供了完整的陀螺仪校准流程，并在校准后允许用户测试控制器的方向感应能力。测试界面显示了实时的陀螺仪数据和欧拉角，使用户能够直观地了解控制器的方向。





2024年10月4日 ****************************************************

今天想把所有的文件功能搞清楚，直接借鉴源代码实现鼠标移动的功能，绕开Build里面无法解决pthread.h的问题。那个涉及到很多修改，我觉得无法解决。
AppStage_ControllerSettings.cpp这个类实现了test orientation的功能。
AppStage_MagnetometerCalibration.cpp这个类实现了具体的功能。





2024年10月2日 ****************************************************

Windows的文件内查找功能非常差，浪费了我很多时间。应该使用命令行工具来查找：像这样。
findstr /s /i /m "pthread" *.cmake CMakeLists.txt


2024年9月29日 ****************************************************  

今天已经可以正常使用navigation controller，通过联通过蓝牙方式进行连接，蓝牙方式连接的时候有超时的问题。不过问题不大，只要保持使用就可以。另外现在我需要实现的是move controller的体感控制这个需要自己写一个后台程序。
通过这么多天的研究，真正连接navigation controller成功的是DShidmini，DSHidmini的连接成功依靠的是修改了inf配置文件中的两行，cainengjiejue lanyalianjiede wenti 。具体的方法咋iGithub对应的讨论中有说明，但是要结合Claude来修改，因为那个说明实在是不清楚。

游戏当中的映射可以通过steam控制器映射。当控制器可以连接到PC的时候并且在游戏控制器里面能够列出navigation controller的时候，那么steam里面也可以成功地进行设置。
那么现在回到以前的第一个问题move controller的映射和指向的配置，我觉得是需要通过PS move service这个库来完成。
那么这个的控制我觉得就要依赖算法目前我觉得Psmoveservice的算法非常好但是我不知道是否能够成功的用到游戏里面。

今天又回到了前面的问题，就是需要把PS move service这个库整个构建出来。因为我想使用这个苦里面的方法和函数。
但是这个库使用到了比较旧的boost，还有比较老的cmake。我想最主要的问题出在1.61版本的boost上面，现在最新的版本是1.81版，老版本的无法下载，不知道为什么。哈哈

有一点进展的是PS move service这个库能够用git clone把所有的第三方包都下载下来，上次不能下载也不知道是网络的原因还是什么。哈哈
我想如果能解决boost的问题应该就可以解决问题。把boost里面的包构建出来以后就可以构建PS move service的库文件，这样子我的方法就可以轻而易举地使用它们。




2024年9月28日 ****************************************************

其实64位版本的DS hid mini是可以通过蓝牙连接的，只不过要克服一些困难老版本的SCPtoolkit会把通用的蓝牙适配器变成专用的navigation controller使用。所以会做出一些牺牲。这是昨天研究的结果。

我决定还是返回64位版本的DS hid mini来尝试使用蓝牙连接，现在的问题是DS4Windows的驱动到底要使用哪一个。






2024年9月27日 ****************************************************  
研究了一圈，又回到了ScpToolkit，DsHidMini的版本似乎是可以使用的，但是对Navigation Controller的支持有问题。

Reddit上有个人说以前使用ScpToolkit是可以连接Navigation Controller的。也可以使用Mayflash Magic NS2蓝牙设备来无线连接手柄。帖子在这里https://www.reddit.com/r/overwatch2/comments/11jqmf6/anybody_else_use_ps3_navigation_controller_on_pc/

测试了一下，无法利用DsHIdmini来正常连接手柄，只能利用Rewasd安装以后Navigation Controller能够连接来检测手柄，估计Rewasd是利用了D4Controller的驱动来连接的。

但是目前没有哪个库可以利用蓝牙来连接PSNC。前面那个人说可以SCPToolkit，但那是32位时代，估计在win10 64bit上也可以，只要运行在32bit模式下就行了。还是要试一下。

D4Controller有几个自带工具可以用一个网页测试PS的两个手柄，非常好用，当然前提是要安装好驱动和连接。PSMC是蓝牙，PSNC是USB有线连接。


2024年9月21日 ****************************************************  
回到Rewasd方案，测试一下能否使用。可以非常好的使用。



2024年9月20日 ****************************************************  

整个PSMoveServiceEx库是32位的。


2024年9月19日 ****************************************************  

千万不要下zip文件去安装一定要用git clone！！！




2024年9月18日 ****************************************************  
一直想使用Sony的sharpshooter来进行FPS游戏，所以做点研究。

今天尝试连接 navigation controller，才发现没有那么容易，索尼并没有公开蓝牙通讯协议。这导致了在连接到pc的时候会出现地址错误。虽然我们可以在蓝牙设其他设备里面看到navigation controller，这并不表示就可以正常使用。
ai提供了scptoolkit这个开源的代码库，但是她太老了。所以又提供了以下这个支持windows10 64bit的开源代码来使用。

https://github.com/nefarius/DsHidMini
今天正在尝试看看是否能识别到Navigation Controller。

但是目前最专业的应该就是rewasd（49美金），有着非常专业的设置和界面，应该可以映射任何设备。所以特地注册了rewasd的账号。

不管怎样，我先试一下免费的工具，如果可以解决问题，则就不用花费29美金去购买强大的rewasd。


22点37分

Navigation Controller的灯一直闪，无法连接上，使用了PS3的蓝牙程序也不行。

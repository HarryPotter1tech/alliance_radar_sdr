# RADAR-SDR

本项目围绕 GFSK 无线链路，完成了从业务数据构造、帧打包、GNU Radio 调制/收发，到后续分析与调试接口的基础流程。

## 环境说明

- `radar-sdr/`
	- 项目使用的 Python 虚拟环境目录。
	- 其中安装当前链路与协议相关依赖（当前重点为 `startrek`、`tcp`、`mqtt`）。
	- 开发或运行前建议先激活该环境，避免本机系统 Python 和项目依赖不一致。

```bash
source radar-sdr/bin/activate
```

## 近期更新（2026-04-22）

- 接收分析链路调整：`analysis/analysis.py` 由原先 ZeroMQ 读取改为 TCP 客户端读取，连接 `127.0.0.1:2000`，并在缓存达到 200 字节后触发解析。
- 协议解析同步：`analysis/frame_parser.py` 中 `0x0A05` 增益帧按 5 组增益（hero/engineer/infantry1/infantry2/sentinel）+ 1 字节 `sentinel_posture` 解析；其中 2 字节子字段按 little-endian 读取。
- GUI 结构变更：`gui/debug_gui.py` 已移除，新增 `gui/sdr_gui.py` 与 `gui/gui_test.py`（当前为占位/初始化状态）。
- 流图与产物更新：`GFSK-loop.grc` 已更新；`launch/package.bin` 随业务帧生成逻辑重新产出。
- 虚拟环境依赖更新：当前 `radar-sdr/` 环境中新增 `startrek`、`tcp` 相关包及对应 `.dist-info` 文件（由终端安装依赖产生）。

## 近期环境调整（2026-04-22 夜间）

- 已从虚拟环境中卸载 `dearpygui`、`pyzmq`、`zmq`，以收敛到当前链路所需依赖。
- 已安装 `mqtt`（`mqtt-0.0.1`），并引入对应脚本与元数据文件。
- 当前 `gui/` 目录下 Python UI 原型文件已移除，后续 UI 将迁移为 Rust 实现。

## 本次更新明细（功能 + 模块）

### 功能更新

- 接收通道重构：接收端由 ZeroMQ 改为 TCP Socket，连接地址统一为 `127.0.0.1:2000`。
- 解析触发策略调整：按分块接收并缓存，缓存达到阈值后触发解析，减少小包频繁解析。
- 解析接口简化：`FrameParser` 改为直接接收输入字节进行 `payload_parse(input_items)`。
- 协议一致性同步：`0x0A05` 仍按 5 组增益 + 1 字节 `sentinel_posture` 解析，2 字节子字段保持 little-endian。
- 数据结构健壮性修复：`RoboMasterInfo` 的列表字段改为 `dataclass field(default_factory=...)`，避免实例共享可变默认值。

### 模块更新

- 修改：`analysis/analysis.py`、`analysis/frame_parser.py`、`GFSK-loop.grc`、`launch/package.bin`。
- 删除：`gui/debug_gui.py`、`gui/sdr_gui.py`、`gui/gui_test.py`。
- 新增：`GFSK_Transmmit_signal.py`、根目录 `package.bin`。
- 环境新增：`radar-sdr/lib/python3.10/site-packages/startrek/`、`radar-sdr/lib/python3.10/site-packages/tcp/`、`radar-sdr/lib/python3.10/site-packages/mqtt-0.0.1.egg-info/`。
- 环境移除：`dearpygui`、`pyzmq`、`zmq` 相关包目录与元数据。

## 目录说明（重点）

### 1) `launch/`：业务消息与链路帧生成

- `message_value_generate.py`
	- 负责构造业务消息。
	- 支持 `manual` 和 `random` 两种模式。
	- 内置 `CRC8/CRC16` 查表计算，按命令字生成多帧数据：
		- `0x0A01` 位置
		- `0x0A02` 血量
		- `0x0A03` 弹量
		- `0x0A04` 经济与占点
		- `0x0A05` 增益
	- 已按协议修正 `0x0A05` 负载结构：去掉不需要的字段，补齐哨兵姿态字节，并统一发送端字节序。

- `frame_generate.py`
	- 负责链路层封装。
	- 每 15 字节业务负载前添加：
		- `access_code`（8 字节）
		- `header_1`（2 字节）
		- `header_2`（2 字节）
	- `transmmit_mode`：
		- `0`：信号链路 access code
		- `1`：干扰链路 access code

- `launch_tofile.py`
	- 生成 `package.bin` 的入口脚本。
	- 先构造业务消息，再封装链路帧并写入二进制文件。

- `launch.py`
	- 项目启动脚本（当前用于生成 `package.bin` 的入口）。

### 2) `gnu radio /`：GFSK 发射/接收流图

- `GFSK_Transmmit_signal.py`
	- 由 GRC 导出的 Python 顶层流图。
	- 关键链路：
		- `file_source` 读取二进制数据
		- `digital.gfsk_mod` 调制
		- `iio_pluto_sink/source` 与 Pluto SDR 交互
		- `digital.gfsk_demod` 解调
		- `zeromq.push_sink` 输出字节流
	- 提供噪声等级选择参数（`noise_1/noise_2/noise_3`）。

- `GFSK-Transmmit-signal.grc`
	- 信号发射与回环观察主流图。

- `GFSK-Transmmit-noise.grc`
	- 干扰发射流图（随机源 + GFSK 调制）。

- `GFSK-Receiver.grc`
	- 接收与解调流图，包含接收侧实验块。

- `GFSK-loop.grc`
	- 环路/联调版本流图（用于联合验证）。

### 3) `analysis/`：接收数据分析

- `analysis.py`
	- 使用 TCP Socket 连接 `127.0.0.1:2000`。
	- 持续接收字节分块并进行缓存，达到阈值后调用帧解析器完成基础打印。
	- 当前作为接收分析入口，后续可继续叠加 CRC 校验、切帧统计和业务分发。

- `frame_parser.py`
	- 负责接收端业务字段解析（当前由上层输入完整待解析负载）。
	- 已按协议同步 `0x0A05` 的字段布局与偏移，包含哨兵姿态字段。

- `frame_divde.py`
	- 预留帧切分脚本（当前为空）。

### 4) `gui/`：可视化调试

- 当前状态：Python 侧 GUI 原型已移除，目录预留。
- 规划：后续整体 UI 将使用 Rust 重写，并作为库（lib）形式引入，通过 MQTT 与链路/分析模块通信。

## 端到端流程

1. `launch/message_value_generate.py` 生成业务层消息。
2. `launch/frame_generate.py` 将业务消息按 15 字节切片并封装链路头。
3. `launch/launch.py` 输出 `package.bin`。
4. `gnu radio /GFSK-Transmmit-signal.grc` 或对应 Python 流图读取 `package.bin`，执行 GFSK 调制并通过 Pluto 发射。
5. 接收端流图完成解调后通过本地 TCP 服务输出。
6. `analysis/analysis.py` 接收并准备后续分析。

## 快速使用（最小路径）

### 1) 生成待发数据

```bash
cd launch
python launch.py
```

成功后会在 `launch/` 下生成 `package.bin`。

### 2) 启动 GNU Radio 流图

可选方式：

- 打开并运行 `gnu radio /GFSK-Transmmit-signal.grc`
- 或直接运行导出脚本 `gnu radio /GFSK_Transmmit_signal.py`

### 3) 启动分析接收

```bash
cd analysis
python analysis.py
```

## 当前状态与注意事项

- `analysis/frame_divde.py` 仍为空，需要补充切帧功能实现。
- Python GUI 原型已下线，后续 UI 方案为 Rust lib + MQTT 通信。
- `analysis.py` 已接入 `FrameParser`，但仍建议后续补上 CRC 校验与异常帧统计。
- GNU Radio 导出脚本中 `blocks_file_source` 路径写为 `.../tool/package.bin`，与当前仓库目录 `launch/package.bin` 可能不一致，运行前请确认并修改。
- 文件与类名存在拼写 `Transmmit`（双 m），属于当前项目命名约定，引用时需保持一致。

## 后续建议

1. 在 `analysis/frame_divde.py` 实现基于 `access_code + header` 的切帧器。
2. 在 `analysis.py` 增加 CRC8/CRC16 校验与命令字分发解析。
3. 设计并落地 Rust UI 库接口，明确与 Python 侧的 MQTT topic、QoS、消息格式约定。
4. 统一 `package.bin` 产物路径，避免 `launch/` 与 `tool/` 的路径分叉。

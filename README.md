# RADAR-SDR

本项目围绕 GFSK 无线链路，完成了从业务数据构造、帧打包、GNU Radio 调制/收发，到后续分析与调试接口的基础流程。

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

- `frame_generate.py`
	- 负责链路层封装。
	- 每 15 字节业务负载前添加：
		- `access_code`（8 字节）
		- `header_1`（2 字节）
		- `header_2`（2 字节）
	- `transmmit_mode`：
		- `0`：信号链路 access code
		- `1`：干扰链路 access code

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
	- 使用 ZeroMQ `REQ` 套接字连接 `tcp://localhost:5555`。
	- 持续接收字节数据并累积到缓冲区（当前仅完成接收骨架）。

- `frame_divde.py`
	- 预留帧切分脚本（当前为空）。

### 4) `gui/`：可视化调试

- `debug_gui.py`
	- GUI 调试入口预留（当前为空）。

## 端到端流程

1. `launch/message_value_generate.py` 生成业务层消息。
2. `launch/frame_generate.py` 将业务消息按 15 字节切片并封装链路头。
3. `launch/launch.py` 输出 `package.bin`。
4. `gnu radio /GFSK-Transmmit-signal.grc` 或对应 Python 流图读取 `package.bin`，执行 GFSK 调制并通过 Pluto 发射。
5. 接收端流图完成解调后通过 ZeroMQ 输出。
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

- `gui/debug_gui.py` 与 `analysis/frame_divde.py` 仍为空，需要补充功能实现。
- `analysis.py` 目前仅持续 `recv`，尚未进行帧同步/切帧/CRC 校验。
- GNU Radio 导出脚本中 `blocks_file_source` 路径写为 `.../tool/package.bin`，与当前仓库目录 `launch/package.bin` 可能不一致，运行前请确认并修改。
- 文件与类名存在拼写 `Transmmit`（双 m），属于当前项目命名约定，引用时需保持一致。

## 后续建议

1. 在 `analysis/frame_divde.py` 实现基于 `access_code + header` 的切帧器。
2. 在 `analysis.py` 增加 CRC8/CRC16 校验与命令字分发解析。
3. 为 `gui/debug_gui.py` 增加实时帧计数、CRC 失败计数、各 cmd_id 字段可视化。
4. 统一 `package.bin` 产物路径，避免 `launch/` 与 `tool/` 的路径分叉。

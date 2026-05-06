# alliance_radar_sdr

本项目围绕 GFSK 无线链路，完成了从业务数据构造、链路帧生成、GNU Radio 调制/解调，到 TCP 解析与外部联调的完整流程。

## 环境说明

- `radar-sdr/`：项目使用的 Python 虚拟环境目录。
- 建议先激活该环境，再运行生成、调试和联调脚本。

```bash
source radar-sdr/bin/activate
```

## 当前架构

### 1. `launch/`：业务数据与链路帧生成

- `message_value_generate.py`：生成业务消息，包含位置、血量、弹量、经济与增益等字段。
- `noisekey_value_gengerate.py`：生成噪声密钥消息，包含 `sdr_behavior` 和 6 个密钥字节。
- `frame_generate.py`：负责链路层封装，每 15 字节负载前添加 `access_code`、`header_1` 和 `header_2`。
- `launch_tofile.py`：离线生成测试文件的入口，会输出 `message_package.bin` 和 `noisekey_package.bin`。

### 2. `gnu radio /`：GFSK 发射/接收流图

- `GFSK_Transmmit_signal.py`：信号侧 GFSK 流图脚本。
- `GFSK_Transmmit-noise.grc` 和 `GFSK_Transmmit_noise.py`：干扰侧链路脚本。
- `GFSK_Receiver.grc`、`Receiver_noise.grc`、`Receiver_noise.py`：接收侧链路脚本。
- 文件名中的 `Transmmit`、`infentry` 等拼写保持了当前项目约定，除非做全局重构，否则不要单独改名。

### 3. `tcp/`：TCP 收发与聚合入口

- `tcp_comm.py`：TCP 连接、断线重连和字节流解析的核心实现。
- `tcp_launch.py`：当前 TCP 联调入口，使用 4 个线程同时启动信号接收、噪声接收、数据中心接收和数据中心发送。

### 4. `parser/`：数据结构解析

- `gnuradio_frame_parser.py`：把 GNU Radio 输出的字节流解析成信号信息和噪声密钥结构。
- `datacenter_package_parser.py`：把数据中心来的雷达标记包解析成 `RadarInfo`。

## 当前端口映射

当前代码里实际使用的端口如下：

- `127.0.0.1:2000`：GNU Radio 信号流输入，解析后更新 `RoboMaster_Signal_Info`
- `127.0.0.1:2500`：GNU Radio 噪声密钥流输入，解析后更新 `RoboMaster_Noise_Key`
- `192.168.1.10:1500`：数据中心回传接收端，解析后更新 `RadarMarkProcess`
- `192.168.1.10:1000`：数据中心转发发送端，向 Unity 或外部客户端发包

如果改动这些端口，必须同步检查 `tcp/tcp_comm.py`、GNU Radio 流图和外部客户端配置。

## 信息结构参考

### `RoboMaster_Signal_Info`

这个结构承载 GNU Radio 信号流解析结果，主要字段分为几类：

- 位置：`hero_position`、`engineer_position`、`infentry_position_1`、`infentry_position_2`、`drone_position`、`sentinel_position`
- 血量：`hero_blood`、`engineer_blood`、`infentry_blood_1`、`infentry_blood_2`、`saven_blood`、`sentinel_blood`
- 弹量：`hero_amnunition`、`infentry_amnunition_1`、`infentry_amnunition_2`、`drone_amnunition`、`sentinel_amnunition`
- 经济与占点：`econmic_remain`、`economic_total`、`occupation_status`
- 增益：`hero_gain`、`engineer_gain`、`infentry_gain_1`、`infentry_gain_2`、`sentinel_gain`、`sentinel_posture`

### `RoboMaster_Noise_Key`

这个结构承载 GNU Radio 噪声密钥流解析结果：

- `sdr_behavior`
- `sdr_key_1` 到 `sdr_key_6`

### `RadarMarkProcess`

这个结构承载数据中心雷达标记状态：

- 敌方状态：`IsOpponentHeroDebuffed`、`IsOpponentEngineerDebuffed`、`IsOpponentInfantry3Debuffed`、`IsOpponentInfantry4Debuffed`、`IsOpponentAerialMarked`、`IsOpponentSentryDebuffed`
- 己方状态：`IsAllyHeroMarked`、`IsAllyEngineerMarked`、`IsAllyInfantry3Marked`、`IsAllyInfantry4Marked`、`IsAllyAerialMarked`、`IsAllySentryMarked`

### `RadarMessageAutoDecisionSynchronization`

这个结构承载数据中心自动决策同步信息：

- `EncryptionRank`
- `IsModifierKeyAble`

### `RadarInfo`

`RadarInfo` 是数据中心解析的组合结果，内部同时包含：

- `radar_mark_process`
- `radar_message_auto_decision_synchronization`

## 端到端流程

1. `launch/message_value_generate.py` 和 `launch/noisekey_value_gengerate.py` 生成业务层消息。
2. `launch/frame_generate.py` 将业务消息按 15 字节切片并封装链路头。
3. `launch/launch_tofile.py` 输出 `message_package.bin` 和 `noisekey_package.bin`。
4. GNU Radio 流图读取对应输入文件，执行 GFSK 调制并通过 Pluto 发射。
5. 接收端流图完成解调后通过本地 TCP 服务输出。
6. `tcp/tcp_launch.py` 启动 TCP 端接收与转发，完成解析入口联调。

## 快速使用

### 1) 生成待发数据

```bash
python launch/launch_tofile.py
```

### 2) 启动 GNU Radio 流图

可选方式：

- 打开并运行 `gnu radio /GFSK-Transmmit-signal.grc`
- 或直接运行导出脚本 `gnu radio /GFSK_Transmmit_signal.py`

### 3) 启动 TCP 联调

```bash
python tcp/tcp_launch.py
```

## 当前状态与注意事项

- `tcp/tcp_comm.py` 已支持断线重连。
- 解析入口已迁移至 `parser/gnuradio_frame_parser.py` 和 `parser/datacenter_package_parser.py`。
- GNU Radio 导出脚本中的文件路径需要和当前仓库目录一致，运行前请确认输入文件位置。
- 文件与类名存在拼写 `Transmmit`（双 m）的情况，属于当前项目命名约定，引用时需保持一致。

## 后续建议

1. 在解析链路中补充基于 `access_code + header` 的切帧器。
2. 在解析器中增加 CRC8/CRC16 校验与命令字分发解析。
3. 统一 GNU Radio 输入文件路径，避免导出脚本与仓库目录分叉。

## 使用系统 GNU Radio（虚拟环境兼容）

如果虚拟环境中无法通过 `pip` 安装 `gnuradio`，可以让虚拟环境使用系统已安装的 GNU Radio 包。

### 临时生效

```bash
export PYTHONPATH=/usr/lib/python3/dist-packages:$PYTHONPATH
/home/pinkpanda/linux-RADAR/RADAR-2026/RADAR-SDR/radar-sdr/bin/python tcp/tcp_launch.py
```

### 永久生效

编辑 `radar-sdr/pyvenv.cfg`，将 `include-system-site-packages = true`，然后重新激活虚拟环境：

```bash
source radar-sdr/bin/activate
```

### 其他选项

也可以使用系统包管理器或 conda 安装 GNU Radio：

```bash
sudo apt update
sudo apt install gnuradio python3-gnuradio
# 或使用 conda:
conda install -c conda-forge gnuradio pyqt
```

如果仓库里有 `init.sh` 并包含 `export PYTHONPATH=...`，也可以直接运行：

```bash
source init.sh
```
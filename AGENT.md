# AGENT.md

## 项目目标

这个仓库实现的是一条完整的通信链路：

`launch/` 负责构造业务数据和链路帧，`gnu radio /` 负责 GFSK 调制/解调与空口收发，`tcp/` 负责把 GNU Radio 侧的数据接入到本地解析和外部客户端，`parser/` 负责把字节流还原成业务结构。

任何涉及协议、字段顺序、字节序、端口号、帧长度或线程模型的修改，都必须同步检查整条链路，不要只改单点。

## 代码入口

- `tcp/tcp_launch.py` 是当前 TCP 联调入口，会同时启动 4 个线程：信号接收、噪声密钥接收、数据中心转发、数据中心回传。
- `tcp/tcp_comm.py` 是 TCP 连接与重连逻辑的核心实现。
- `launch/launch_tofile.py` 是离线生成测试包的入口。
- `gnu radio /GFSK_Transmmit_signal.py`、`gnu radio /GFSK_Receiver.py`、`gnu radio /Receiver_noise.py` 是 GNU Radio 导出的流图脚本。

## 通信架构

### 1. 业务数据生成

`launch/message_value_generate.py` 和 `launch/noisekey_value_gengerate.py` 负责生成业务层字段。

`launch/frame_generate.py` 负责把业务负载切成链路帧，并在每 15 字节负载前加统一头部。

### 2. GNU Radio 侧

`gnu radio /` 下的脚本负责把二进制数据做 GFSK 调制、发射、接收、解调，再通过本地 TCP 端口把数据吐给 Python 侧。

这部分文件名里保留了当前项目的拼写习惯，尤其是 `Transmmit` 的双 m 命名，不要在不做全局同步的情况下改名。

### 3. TCP 聚合层

`tcp/tcp_comm.py` 采用“谁发数据，谁定规则”的设计：

- GNU Radio 信号流使用本地回环地址和流式缓冲，解析到 `RoboMaster_Signal_Info`。
- GNU Radio 噪声密钥流使用本地回环地址和流式缓冲，解析到 `RoboMaster_Noise_Key`。
- 数据中心回传使用独立连接和固定频率的包式收发。
- 数据中心转发使用固定地址和端口，把当前内存里的信号/密钥组合后发给 Unity 或外部客户端。

### 当前端口映射

当前代码里实际使用的端口如下：

- `127.0.0.1:2000`：GNU Radio 信号流输入，解析后更新 `RoboMaster_Signal_Info`
- `127.0.0.1:2500`：GNU Radio 噪声密钥流输入，解析后更新 `RoboMaster_Noise_Key`
- `192.168.1.10:1500`：数据中心回传接收端，解析后更新 `RadarMarkProcess`
- `192.168.1.10:1000`：数据中心转发发送端，向 Unity 或外部客户端发包

这些端口是联调约定的一部分，修改时必须同步检查 GNU Radio 脚本和 TCP 入口。

### 4. 解析层

`parser/gnuradio_frame_parser.py` 负责把 GNU Radio 输出的字节流解析成 `RoboMaster_Signal_Info` 和 `RoboMaster_Noise_Key`。

`parser/datacenter_package_parser.py` 负责把数据中心来的雷达标记包解析成 `RadarInfo`。

## 信息结构参考

### `RoboMaster_Signal_Info`

这个结构承载 GNU Radio 信号流解析结果，主要字段分四类：

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

### 字段同步提醒

这些结构的字段顺序、默认值和字节序，和 `launch/` 造包逻辑以及 `parser/` 解析逻辑是绑定的。只改结构定义而不改打包/解析代码，会直接造成链路不一致。

## 修改约束

### 协议必须联动

如果修改以下任意一项，必须同步检查生成端、接收端和解析端：

- 命令字 `cmd_id`
- 帧头结构
- 字段数量或字段顺序
- 字节序
- 端口号和 IP 地址
- 单包长度和缓存触发阈值

### 并发模型不要局部改写

当前 `tcp/tcp_launch.py` 使用共享对象加 `threading.Lock()` 的方式把四个通道串起来。修改时要保持：

- 共享对象的语义不变
- 锁保护范围尽量小，但不能破坏原子更新
- 重连逻辑仍然要保留

### 不要破坏现有命名

仓库里存在一些拼写不统一但已经被代码引用的名字，例如：

- `Transmmit`
- `infentry`
- `amnunition`
- `saven_blood`

除非你准备做全局重构并同步所有引用，否则不要单独修正这些名字。

## 编辑时优先检查的文件

当任务和通信链路有关时，优先查看这些文件：

- `tcp/tcp_launch.py`
- `tcp/tcp_comm.py`
- `parser/gnuradio_frame_parser.py`
- `parser/datacenter_package_parser.py`
- `launch/frame_generate.py`
- `launch/message_value_generate.py`
- `launch/noisekey_value_gengerate.py`

## 运行与验证

建议先激活仓库自带虚拟环境，再做联调：

```bash
source radar-sdr/bin/activate
```

常用验证顺序：

1. 先生成离线包，确认 `launch/` 的打包逻辑没有坏。
2. 再启动 GNU Radio 流图，确认端口和数据流能起来。
3. 最后跑 `tcp/tcp_launch.py`，确认四个线程能同时启动并持续重连。

如果你改的是协议字段或缓冲长度，优先做端到端联调，而不是只看单文件语法。

## 处理原则

- 尽量改最小必要范围。
- 不要凭空重写整条链路。
- 优先维护当前 wire protocol 的兼容性。
- 如果发现架构说明和代码实现不一致，以代码实现为准，再回头更新文档。
# alliance_radar_sdr

本项目围绕 GFSK 无线链路，实现了从业务数据构造、链路帧生成、GNU Radio 调制/解调，到信号解析与 ZMQ 联调的数据通道。

## 环境说明

- `radar-sdr/`：项目使用的 Python 虚拟环境目录。
- 建议先激活该环境，再运行生成、调试和联调脚本。

```bash
source radar-sdr/bin/activate
```

## 干扰密钥机制

比赛双方各在雷达基座上放置一台干扰源，发射**对方**的干扰波。系统里跑着两条链路：

| 链路 | 内容 | 用途 |
|------|------|------|
| 信号波 | 对方机器人的位置、血量等业务数据 | 获取战场信息 |
| 干扰波 | 一个 6 字节的加密密钥 | 互相压制对方的雷达标记效果 |

### 核心规则

> 谁解出的对方干扰波难度更高，谁的机器就免疫对面的易伤。

### 以红方视角为例

1. 红方雷达持续接收并解析**蓝方**干扰波的密钥
2. 每成功解出一次，**蓝方干扰波等级 +1**
3. 同时，蓝方也在解析红方的干扰波，红方干扰等级也会涨
4. 一段时间后，看双方谁解出来的对方干扰等级更高：
   - 蓝方干扰等级 **>** 红方 → 红方解得快 → 蓝方的雷达标记对红方机器无效（不产生易伤/双倍易伤）
   - 红方干扰等级 **>** 蓝方 → 蓝方解得快 → 红方的雷达标记对蓝方机器无效

本质是拼解密速度。**你能把对方的密钥解到比对方解你的更高，你就免疫对面的易伤压制。**

### 代码流程

```
[蓝方干扰波空口信号]
        │ GNU Radio 解调
        ▼
TCP :2500 ──▶ tcp_gnuradio_noise_key_receiver
                    │ 解析 6 字节密钥
                    ▼
              RoboMaster_Noise_Key
              (sdr_key_1 ~ sdr_key_6)
                    │
                    ▼
              ZMQ PUB :5555 ──▶ radar-egui 上报
```

## 当前架构

### 1. `launch/`：业务数据与链路帧生成

- `message_value_generate.py`：离线生成信号测试包（位置、血量、弹药、经济、增益）。
- `noisekey_value_gengerate.py`：离线生成噪声密钥测试包。
- `crc_table.py`：CRC8/CRC16 查找表，供生成器使用。
- `frame_generate.py`：链路层封装，每 15 字节负载前添加 `access_code`、`header_1` 和 `header_2`。
- `launch_tofile.py`：离线生成测试文件的入口，输出 `message_package.bin` 和 `noisekey_package.bin`。

### 2. `gnu radio /`：GFSK 发射/接收流图

- `GFSK_Transmmit_signal.py`：信号侧 GFSK 流图脚本。
- `GFSK_Transmmit_noise.py`：噪声侧 GFSK 流图脚本。
- `GFSK_Receiver_Noise.py`：噪声侧接收流图（当前噪声模式运行）。
- `GFSK_Receiver_Signal.py`：信号侧接收流图（预留）。

### 3. `tcp/`：TCP 收发

- `tcp_comm.py`：TCP 连接、断线重连和噪声密钥字节流解析。

### 4. `control/`：GNU Radio 线程控制

- `gnuradio_control.py`：启动 GNU Radio 接收流图，轮询 `shared_state` 更新噪声等级参数。

### 5. `parser/`：数据结构解析

- `gnuradio_frame_parser.py`：把 GNU Radio 输出的字节流解析成 `RoboMaster_Signal_Info` 和 `RoboMaster_Noise_Key`。

## 当前端口映射

| 端口 | 方向 | 用途 |
|------|------|------|
| `127.0.0.1:2000` | GNU Radio → Python | 信号流输入（预留） |
| `127.0.0.1:2500` | GNU Radio → Python | 噪声密钥流输入 |
| `tcp://*:5555` | Python → radar-egui | ZMQ PUB，发布 SDR 数据（计划中） |

## 信息结构参考

### `RoboMaster_Signal_Info`

承载 GNU Radio 信号流解析结果：

| 类别 | 字段 |
|------|------|
| 位置 | `hero_position`、`engineer_position`、`infantry_3_position`、`infantry_4_position`、`aerial_position`、`sentry_position` |
| 血量 | `hero_blood`、`engineer_blood`、`infantry_3_blood`、`infantry_4_blood`、`reserved`、`sentry_blood` |
| 弹药 | `hero_ammo`、`infantry_3_ammo`、`infantry_4_ammo`、`aerial_ammo`、`sentry_ammo` |
| 经济 | `remaining_gold`、`total_gold`、`occupation_status` |
| 增益 | `hero_gain` ~ `sentry_gain`（每组 7 字节）、`sentry_posture`、`hero_gain_state` ~ `sentry_gain_state` |

### `RoboMaster_Noise_Key`

承载 GNU Radio 噪声密钥流解析结果：`sdr_behavior` + `sdr_key_1` ~ `sdr_key_6`（各 1 字节）。

## 端到端流程

1. `launch/launch_tofile.py` 生成 `message_package.bin` 和 `noisekey_package.bin`。
2. GNU Radio 流图读取输入文件，执行 GFSK 调制并通过 Pluto 发射。
3. 接收端流图完成解调后通过本地 TCP 服务输出。
4. `thread_init.py` 启动线程入口，完成 TCP 接收与 GNU Radio 控制。

## 快速使用

### 1) 生成测试数据

```bash
python launch/launch_tofile.py
```

### 2) 启动 GNU Radio 流图

```bash
python "gnu radio /GFSK_Transmmit_signal.py"
```

### 3) 启动联调

```bash
python thread_init.py --side red
```

> `--side` 为**我方阵营**（red / blue）。SDR 接收己方雷达基座放置的波源
> （信息波 433.2/433.92 MHz、干扰波对应频段），波内携带对方数据（规则手册 5.6）。
> 旧参数 `--enemySide` 已废弃（仍兼容，勿再使用）。

## 使用系统 GNU Radio（虚拟环境兼容）

```bash
export PYTHONPATH=/usr/lib/python3/dist-packages:$PYTHONPATH
source radar-sdr/bin/activate
python thread_init.py
```

（已启用 `include-system-site-packages = true`）

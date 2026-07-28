# RADAR-SDR 接口清理 TODO

基于 [radar-egui](https://github.com/Alliance-Algorithm/radar-egui) 2026-07 重构对比分析

## 背景

radar-egui 已完成重大重构：
- SDR 数据接入由 TCP `127.0.0.1:2000` 二进制 → **ZMQ SUB `tcp://127.0.0.1:5555` JSON**
- `src/sdr/` 目录已删除，`tcp_client.rs` / `RoboMasterSignalInfo` 已废弃
- Unity `RADAR_APP` 路径已由 `alliance_radar_location_lidar` ROS2 替代
- ZMQ PUB on `tcp://*:5557` 发布 GameState / RadarMarkProcess

## 已清理项

### 1. 移除 Unity TCP 转发 (tcp_datacenter_transmitter)

- [x] **删除 `tcp/tcp_comm.py`** 中的 `tcp_datacenter_transmitter()` 函数
- [x] **删除 `thread_init.py`** 中的 transmitter 线程创建与启动
- [x] **删除 `thread_init.py`** 中对 `tcp_datacenter_transmitter` 的 import

### 2. 移除数据中心回传 (tcp_datacenter_receiver)

- [x] **删除 `tcp/tcp_comm.py`** 中的 `tcp_datacenter_receiver()` 函数
- [x] **删除 `thread_init.py`** 中 receiver 线程创建、start、join
- [x] **删除 `parser/datacenter_package_parser.py`** 文件
- [x] **清理** `tcp/tcp_comm.py` 和 `thread_init.py` 中所有相关 import

### 3. 修复启动脚本

- [x] **修复 `start-sdr.sh`**: `tcp_launch.py` → `thread_init.py`

## 待处理

### 4. 数据字段适配（为后续 ZMQ PUB 做准备）

radar-egui 的 `ReceiveSdr` 结构与当前 `RoboMaster_Signal_Info` 存在以下差异，需在 ZMQ 序列化时处理：

| 维度 | 当前 RADAR-SDR | radar-egui 期望 | 动作 |
|------|---------------|-----------------|------|
| 位置类型 | unsigned `[x, y]` | `i16` | 序列化时按 signed 处理 |
| 步兵命名 | `infentry_position_1/2` | `infantry_3/4` | 字段名映射 |
| 血量 | 6 字段含 `saven_blood` | 6 字段: `infantry_3_blood`, `infantry_4_blood`, `reserved`, `sentry_blood` | 重排字段，`reserved` 填 0 |
| 弹药 | `hero_amnunition`, `drone_amnunition` | `hero_ammo`, `aerial_ammo` | 字段名映射 |
| 增益长度 | 36 字节 (5 robots × 5 fields + 1 posture) | **41 字节** (新增 5 个 `robot_state` 字段) | 解析/生成时补齐 |
| 密钥 | `sdr_behavior` + `sdr_key_1..6` | `key: [u8; 6]` | 不再发送 behavior |

### 5. 新增 ZMQ PUB

- [ ] 新增 ZMQ PUB 线程，绑定 `tcp://*:5555`，按 radar-egui `SdrMsg` JSON 格式发布
- [ ] `requirements.txt` 添加 `pyzmq` 依赖

### 6. 保留的内部接口

| 接口 | 端口 | 用途 |
|------|------|------|
| GNU Radio 噪声 | `127.0.0.1:2500` | 噪声密钥流 |
| GNU Radio 信号 | `127.0.0.1:2000` | 信号流解析（数据源） |

### 7. 后续评估

- [ ] ZMQ SUB `tcp://127.0.0.1:5557` — radar-egui → SDR (GameState/RadarMark)
- [ ] 更新 `AGENT.md` / `README.md` 中端口映射文档

# 钱包—RPC 隐私泄露实证测量项目

## 1. 项目背景
在以太坊等 EVM 生态中，用户钱包（例如 MetaMask）通常不会自己维护完整节点，而是通过第三方或公共的 RPC（JSON-RPC）端点读取链上数据、模拟合约调用、广播交易等。  
这带来了潜在隐私风险：RPC 服务提供商（以及网络路径中的观察者）可能基于请求的元数据与语义信息（例如 method、时间戳、请求频率、是否包含地址参数等）对用户行为进行画像，甚至进行多地址关联（linkability）推断。

本项目目标是对上述风险进行“实证测量（empirical measurement）”：通过可复现实验框架在不同 RPC provider 上执行相同负载，收集结构化日志并计算指标，用数据支撑分析结论。

---

## 2. 研究目标（Problem Statement）
本项目旨在测量并量化“钱包通过 RPC 请求可能泄露的隐私信息类型与程度”，并比较不同 RPC provider 在以下维度上的差异：
- 可用性：成功率、超时率、错误类型
- 性能：请求延迟分布（median/avg/max 等）
- 隐私暴露代理指标（proxies）：
  - method 分布（用户在做什么行为）
  - 是否出现地址型请求（has_address）
  - 请求频率/节奏（行为特征）

---

## 3. 范围界定（Scope）
当前 Milestone 1 阶段的范围聚焦于：
- 网络：Sepolia 测试网（chain_id = 11155111）
- 请求场景（scenarios）：
  - `blocknumber`：调用 `eth_blockNumber`（无地址参数，用于连通性/性能基准）
  - `balance`：调用 `eth_getBalance`（包含地址参数，用于地址暴露代理）
- 对比对象：至少两个不同 RPC endpoint（providerA/providerB）
- 数据输出：JSONL（每行一条 RPC 请求记录）

不在 Milestone 1 强制范围内（可作为后续扩展）：
- 交易广播、DeFi/NFT 合约交互、WebSocket 订阅
- 抓包/代理分析（Wireshark/mitmproxy）获取网络层元数据
- 复杂多地址关联算法与评分模型

---

## 4. 威胁模型（Threat Model v1，简要）
潜在攻击者/观察者：
- RPC 服务提供商（记录请求、聚合行为）
- 网络监听者/中间人（观察请求时序与连接信息）
- 恶意 RPC 节点运营者（主动收集与分析）
- 数据分析公司（跨站/跨服务关联）

主要攻击向量（本项目当前可测的部分）：
- 元数据泄露：请求时间戳、频率、延迟、错误特征
- 语义泄露：method 类型、是否包含地址/合约调用痕迹
- 关联推断：同一来源的多地址访问模式（后续扩展）

---

## 5. 测量框架（Measurement Harness）是什么
本项目实现了一个“可复现实验 harness”，用于：
- 读取配置文件（YAML）：指定 network、rpc_url、scenario、duration、interval 等
- 自动发起 JSON-RPC 请求：如 `eth_blockNumber`、`eth_getBalance`
- 记录每次请求的关键元数据到 JSONL 日志
- 对不同 provider 运行相同负载，实现 A/B 对比
- 使用 `summarize.py` 对日志进行汇总统计

一句话：harness = “一键重复跑实验 + 产出可分析数据”的自动化框架。

---

## 6. 项目结构
- `configs/`
  - `exp_sepolia_providerA.yaml`：Provider-A 实验配置
  - `exp_sepolia_providerB.yaml`：Provider-B 实验配置
  - `addresses_demo.txt`：余额查询用地址列表（每行一个 0x... 地址）
- `src/`
  - `runner.py`：实验入口，读取 config，循环运行场景并写日志
  - `rpc_client.py`：JSON-RPC 客户端（HTTP）
  - `scenarios.py`：场景定义与参数构造
  - `logger.py`：构造日志记录并写入 JSONL
  - `summarize.py`：汇总日志并输出指标
- `logs/`
  - 运行生成的 JSONL（建议默认忽略或仅提交脱敏样例）

---

## 7. 配置说明（示例）
### 7.1 Blocknumber 场景（基准）
```yaml
provider_id: providerA
chain_id: 11155111
rpc_url: "https://ethereum-sepolia-rpc.publicnode.com"
scenario: "blocknumber"
duration_s: 30
interval_s: 2
out_log: "logs/run_providerA.jsonl"

# Code_Interpreter_Agent 🤖
基于 LangChain + DeepSeek 实现的自动化数据分析 AI Agent，让你用自然语言直接查询和分析电信用户数据集（telco_data.csv）。

---

## ✨ 项目特性
- **自然语言交互**：用中文提问，自动生成 pandas 代码并执行
- **多维度分析**：支持统计、筛选、分组、对比等复杂数据分析
- **代码安全执行**：基于 PythonAstREPL 沙箱环境，安全运行代码
- **结构化输出**：自动返回问题摘要、执行代码、分析结果
- **开箱即用**：完整依赖配置，一键部署运行

---

## 🚀 快速开始

### 1. 克隆项目
```bash
git clone https://github.com/xull0924/Code_Interpreter_Agent.git
cd Code_Interpreter_Agent
2. 安装依赖
bash
运行
pip install -r requirements.txt
3. 配置环境变量
在 PowerShell 中设置你的 DeepSeek API Key（不要硬编码到代码中）：
powershell
$env:DEEPSEEK_API_KEY = "你的 DeepSeek API Key"
如果你需要指定数据集路径，可以额外设置：
powershell
$env:TELCO_CSV_PATH = "D:\你的路径\telco_data.csv"
4. 运行项目
bash
运行
python generate_code_agent.py
默认会执行示例问题："计算 MonthlyCharges 字段的均值"，你也可以修改 main() 函数中的 question 变量来提问其他问题。
📊 支持的分析示例
你可以向 Agent 提出以下类型的问题：
基础统计："计算 MonthlyCharges 字段的均值和中位数"
多条件筛选："找出开通了在线安全服务但流失的用户数量"
分组对比："按合同类型分组，统计每组的流失率"
业务洞察："分析在网时长与流失率的关系"
📁 项目结构
plaintext
Code_Interpreter_Agent/
├── generate_code_agent.py    # 主代码文件：Agent 核心逻辑
├── telco_data.csv            # 电信用户数据集
├── requirements.txt          # 项目依赖清单
├── .gitignore                # Git 忽略文件配置
└── README.md                 # 项目说明文档
🛠️ 技术栈
大模型：DeepSeek Chat (deepseek-chat)
框架：LangChain (Agent + Tool 调用)
数据分析：Pandas
代码执行：PythonAstREPLTool (沙箱


from __future__ import annotations
import os
from pathlib import Path

import pandas as pd
from pydantic import BaseModel, Field

from langchain.agents import create_agent
from langchain.tools import tool
from langchain_deepseek import ChatDeepSeek
from langchain_experimental.tools import PythonAstREPLTool

# -----------------------------
# 1) 初始化大模型（DeepSeek）
# -----------------------------

def build_model() -> ChatDeepSeek:
	"""
	创建 DeepSeek Chat 模型实例。
	"""
	api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
	if not api_key:
		raise RuntimeError(
			"缺少环境变量 DEEPSEEK_API_KEY。\n"
			"请先在 PowerShell 设置：$env:DEEPSEEK_API_KEY = '你的key'"
		)

	base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com").strip()

	return ChatDeepSeek(model="deepseek-chat", api_key=api_key, base_url=base_url)


model = build_model()


# -----------------------------
# 2) 读取数据（telco DataFrame）
# -----------------------------

def load_telco() -> pd.DataFrame:
	"""
	读取 telco_data.csv，并返回 DataFrame。
	"""
	env_path = os.getenv("TELCO_CSV_PATH", "").strip()
	if env_path:
		csv_path = Path(env_path).expanduser().resolve()
	else:
		csv_path = Path(__file__).resolve().parent / "telco_data.csv"

	if not csv_path.exists():
		raise FileNotFoundError(
			f"找不到 telco_data.csv：{csv_path}\n"
			"解决办法：\n"
			"- 把 telco_data.csv 放到 generate_code_agent.py 同目录；或\n"
			"- 设置环境变量 TELCO_CSV_PATH 为实际路径。"
		)

	df = pd.read_csv(csv_path)

	# 仅影响显示（比如 print(df.head()) 时每列字符串最多显示多少字符），不改变数据本身
	pd.set_option("max_colwidth", 50)
	return df


telco = load_telco()

# -----------------------------
# 3) 准备“代码解释器工具” ast
# -----------------------------
# PythonAstREPLTool 的作用：
# - 你给它一段字符串形式的 Python 代码，它会执行。

ast = PythonAstREPLTool(locals={"telco": telco})

# 快速自检：让工具算一个简单值，确认工具能访问 telco
# ast_ans = ast.invoke("telco['SeniorCitizen'].mean()")
# res = telco["SeniorCitizen"].mean()
# print(f"[check] tool mean(SeniorCitizen) = {ast_ans}")
# print(f"[check] pandas mean(SeniorCitizen) = {res}")

# -----------------------------
# 4) 工具：write_formula（把中文问题变成 pandas 代码公式）
# -----------------------------

class WriteFormulaFormat(BaseModel):
	"""约束模型输出格式：只输出一段代码字符串。"""

	search_formula: str = Field(
		..., description="只允许使用 pandas 和 Python 内置库；只返回代码，不要解释。"
	)


@tool
def write_formula(query: str) -> str:
	"""根据用户的自然语言问题，生成可执行的 pandas 代码（只返回代码）。"""

	system_prompt = """
    你是一位专业的数据分析师：
    1. 你可以访问名为 `telco` 的 pandas 数据表。
    2. 根据用户问题，编写 Python 代码回答。
    3. 只允许使用 pandas 和 Python 内置库。
    4. 只返回代码，不返回任何解释文字。
    """.strip()

	# conversation：把 system + user 组成消息
	conversation = [
		{
			"role": "system",
			"content": """
            你可以访问名为 `telco` 的 pandas 数据表。
            请根据用户问题，生成计算所需的 Python 代码：
            - 只返回代码
            - 只用 pandas + 内置库
            """.strip(),
		},
		{"role": "user", "content": query},
	]

	# f_agent：只负责“生成公式代码”的小 Agent
	f_agent = create_agent(
		model=model,
		tools=[ast],
		system_prompt=system_prompt,
		response_format=WriteFormulaFormat,
	)

	formula_res = f_agent.invoke({"messages": conversation})
	return formula_res["structured_response"].search_formula


# -----------------------------
# 5) 主 Agent：生成 + 执行 + 返回结构化结果
# -----------------------------

class ResFormat(BaseModel):
	"""最终输出：问题摘要、公式、结果。"""

	query: str = Field(..., description="对用户问题做精炼总结")
	formula: str = Field(..., description="用于计算的 pandas 代码")
	result: str = Field(..., description="执行公式得到的结果")


SYSTEM_PROMPT = """
    你是一位专业的数据分析师：
    1) 你可以访问名为 `telco` 的 pandas 数据表。
    2) 先生成用于回答问题的 Python 代码（只用 pandas + 内置库）。
    3) 把代码交给 ast（PythonAstREPLTool）执行，得到结果。
    4) 用结构化格式返回：query / formula / result。
    """.strip()


agent = create_agent(
	model=model,
	tools=[ast, write_formula],
	system_prompt=SYSTEM_PROMPT,
	response_format=ResFormat,
)


if __name__ == "__main__":
	
	question = "我有一张表，名为 telco，分别统计：有伴侣、有孩子、既有伴侣又有孩子这三类用户的流失率。"

	response = agent.invoke({"messages": [{"role": "user", "content": question}]})

	sr = response["structured_response"]
	print("\n=== Agent Answer ===")
	print("query  :", sr.query)
	print("formula:", sr.formula)
	print("result :", sr.result)


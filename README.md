# 智能医疗导诊系统

## 项目背景
- 面向中文用户的症状自助导诊与健康建议生成。
- 集成知识库检索、候选疾病概率评估与结构化医疗建议输出。
- 前后端一体：后端 Flask + LangChain，前端 Streamlit。

## 项目目标
- 提供安全、可解释的医疗建议，避免不合规内容。
- 支持查询历史与性能统计，持续优化用户体验。
- 通过环境变量控制模型与参数，便于切换与部署。

## 项目效果
- 候选疾病概率分析与最佳候选自动推荐。
- 结构化建议（评估、立即措施、就医建议、监测要点、紧急处理）。
- 查询历史保存与展示；统计页显示样本数、平均耗时、P95、最大值。

## 核心功能
- 症状匹配与知识库整合（指南、风险）。
- LLM 结构化输出解析与稳健 JSON 处理（容错截断与包裹）。
- 查询历史持久化（含服务耗时与端到端总耗时）。
- 恶意/不合规与非医疗表达检测与统计。

## 安装步骤
1. 准备 Conda 环境（项目规则：环境名为 `llm_pro`）
   - `conda create -n llm_pro python=3.10 -y`
   - `conda activate llm_pro`
   - `pip install -r requirements.txt`（如无文件，按需安装 `langchain`, `python-dotenv`, `streamlit`, `flask`, `requests` 等）
2. 配置环境变量（不提交到 GitHub）
   - 在项目根创建 `.env`（本地使用，已在 `.gitignore` 中忽略）：
     ```
     # LLM模型与服务
     DEEPSEEK_MODEL=deepseek-chat
     DEEPSEEK_API_KEY=YOUR_LOCAL_KEY
     DEEPSEEK_API_URL=https://api.deepseek.com
     TEMPERATURE=0.7
     MAX_TOKENS=250

     # Flask服务
     HOST=0.0.0.0
     PORT=5000
     FLASK_ENV=development
     ```
   - Windows 也可用临时会话变量：`$env:DEEPSEEK_API_KEY="YOUR_LOCAL_KEY"`
3. 启动服务（务必在 `llm_pro` 环境）
   - 后端：`conda activate llm_pro && python app.py`
   - 前端：`conda activate llm_pro && streamlit run streamlit_app.py`
4. 访问前端（默认）
   - 浏览器打开：`http://localhost:8501`

## 使用说明
- 在“症状查询”页填写症状与患者信息，点击“获取医疗建议”。
- “查询历史”支持本地刷新与从服务刷新；显示服务耗时与端到端总耗时。
- “恶意统计”页展示正常/不合规/非医疗次数与性能统计指标。

## 常见问题与经验
- 问题1：最大 token 导致 JSON 截断报错
  - 现象：LLM输出被截断，JSON解析失败。
  - 处理：服务端与解析器均做了容错（尝试提取最外层 `{...}`），并在前端解析失败时回退为空对象；建议适当调高 `MAX_TOKENS`。
- 问题2：Python 环境在 PyCharm 中创建更稳定
  - 经验：部分 IDE 的虚拟环境与包管理存在兼容差异；推荐在 PyCharm 中新建并绑定 `llm_pro`，或统一用 Conda 管理依赖。
- 问题3：模型效果差异
  - DeepSeek、Kimi 表现一般；GPT-5 高速且准确度高。若出现响应变慢，可能超出缓存或上下文上限，切换新窗口可恢复性能。

## 安全与合规
- `.env` 已加入 `.gitignore`，不会提交到 GitHub。
- 代码不记录或输出密钥，仅通过环境变量注入到运行时。
- 历史文件写入使用临时文件 + 原子替换，减少损坏风险。

## 目录与数据
- 历史数据默认在 `logs/query_history.json`（若不存在，前端读取时回退到根目录）。
- 日志位于 `logs/`，包含运行与LLM调用信息，便于排查。

## 验收标准
- 本地 `.env` 生效，Git 提交不会包含 `.env` 与历史日志。
- 前端“查询历史”可正确显示与刷新历史记录。
- 性能统计指标在“恶意统计”页可见（样本数、平均、P95、最大）。

## 贡献与维护建议
- 统一模型配置通过 `.env` 切换；必要时调整 `MAX_TOKENS` 避免截断。
- 统一在 `llm_pro` 环境中运行后端与前端，减少依赖冲突。
- 如需切换到 GPT-5，高速模式可设置 `DEEPSEEK_MODEL=gpt-5-high` 并配置对应的 `DEEPSEEK_API_URL` 与 KEY。

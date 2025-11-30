# 项目规则配置

## Conda环境配置
- **环境名称**: llm_pro
- **所有Python命令**必须在 `llm_pro` Conda环境中执行
- **依赖安装**: 使用 `conda activate llm_pro && pip install`
- **服务启动**: 使用 `conda activate llm_pro && python app.py`

## 启动脚本要求
- 所有批处理脚本必须首先激活正确的Conda环境
- 依赖检查需要在正确的环境中进行
- 服务启动必须在正确的环境中执行

## 开发规范
- 优先使用Conda环境管理依赖
- 确保所有开发工具都在正确的环境中运行
- 记录所有环境特定的配置要求
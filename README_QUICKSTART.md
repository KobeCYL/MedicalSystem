# 🏥 医疗导诊系统 - 快速启动指南

## 📋 系统概述

这是一个基于AI的智能医疗导诊系统，集成DeepSeek大模型，提供症状分析、疾病建议和医疗指导。

## 🚀 一键启动

### 方法一：完整环境设置（推荐）
```bash
# 1. 运行环境设置脚本
setup_env.bat

# 2. 配置API密钥（编辑.env文件）
# 将 your_deepseek_api_key_here 替换为您的实际DeepSeek API密钥

# 3. 启动系统
start.bat
```

### 方法二：手动步骤
```bash
# 1. 创建虚拟环境
python -m venv venv

# 2. 激活虚拟环境
venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量
# 复制 .env.example 为 .env 并配置API密钥

# 5. 启动后端
python app.py

# 6. 启动前端（新终端）
streamlit run streamlit_app.py
```

## 🔑 API密钥配置

1. 获取DeepSeek API密钥：https://platform.deepseek.com
2. 编辑 `.env` 文件：
```env
MODEL=deepseek-chat
API_KEY=您的实际API密钥
API_URL=https://api.deepseek.com/v1
```

## 🌐 访问地址

- **后端API**: http://127.0.0.1:5000
- **前端界面**: http://localhost:8501
- **健康检查**: http://127.0.0.1:5000/health

## 📁 项目结构

```
day_06/
├── app.py                 # Flask后端主程序
├── streamlit_app.py       # Streamlit前端界面
├── requirements.txt       # Python依赖包
├── start.bat             # 一键启动脚本
├── setup_env.bat         # 环境设置脚本
├── .env                  # 环境配置文件
├── data/                 # 数据文件
│   ├── symptom.json      # 症状数据库
│   ├── guideline.json    # 治疗指南
│   └── disease_info.json # 疾病信息
├── models/               # 数据模型
│   └── medical_models.py # Pydantic模型定义
├── services/             # 服务层
│   ├── llm_service.py    # AI服务
│   ├── file_storage_service.py # 文件存储
│   └── security_service.py     # 安全服务
├── controllers/          # 控制器层
│   └── medical_controller.py   # 医疗逻辑控制
├── utils/                # 工具类
│   └── output_parsers.py       # 输出解析器
└── logs/                 # 日志目录
```

## ⚡ 快速测试

### API测试
```bash
curl -X POST http://127.0.0.1:5000/api/medical/query \
  -H "Content-Type: application/json" \
  -d '{"symptom": "头痛发烧", "patient_info": {"age": 30, "gender": "male"}}'
```

### 健康检查
```bash
curl http://127.0.0.1:5000/health
```

## 🛠️ 开发命令

```bash
# 激活虚拟环境
venv\Scripts\activate

# 安装新依赖
pip install <package-name>
pip freeze > requirements.txt

# 代码格式化
black .

# 代码检查
flake8 .

# 类型检查
mypy .
```

## 📝 常见问题

### Q: 启动时显示"API密钥错误"
A: 请检查 `.env` 文件中的 `API_KEY` 配置是否正确

### Q: 前端无法连接后端
A: 确保后端服务已启动（端口5000），检查防火墙设置

### Q: 依赖安装缓慢
A: 可以考虑使用国内镜像源：
```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Q: 内存不足
A: Streamlit和Flask同时运行需要约1GB内存，建议关闭其他程序

## 🔧 故障排除

1. **端口冲突**: 修改 `.env` 中的 `FLASK_PORT` 和 Streamlit 端口
2. **依赖问题**: 删除 `venv` 文件夹重新运行 `setup_env.bat`
3. **API限制**: 检查DeepSeek API的调用频率和配额限制

## 📞 支持

如有问题，请检查日志文件 `logs/system_*.log` 或联系开发团队。
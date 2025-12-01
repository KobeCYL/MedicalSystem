# 版本二实施计划与进度

## 总目标与范围
- 将现有前端迁移为 Next.js/React，在 Vercel 上一体化部署。
- 后端 API 使用 Python Serverless Functions（Vercel）。
- 历史、统计、画像与安全事件统一存储在 Supabase（Postgres）。

## 任务清单与进度
- [x] 初始化 v2 目录与计划文档
- [x] 添加 Serverless 函数骨架与路由配置（v2/vercel.json、v2/api/*）
- [x] 添加 Supabase 表结构 SQL 与环境示例（v2/db/schema.sql、v2/.env.example）
- [x] 规范 medical_query 返回体与入库字段映射（status/耗时/画像）
- [x] Supabase 客户端分页与总数解析（Range + Content-Range）
- [x] CORS 基础头部添加（health/history/stats/medical_query）
- [x] 本地验收脚本完善（success/no_match/failed），降级路径写读验证
- [ ] Next.js 前端骨架创建与页面路由（/、/history、/stats）
- [ ] Python Serverless 写库逻辑接入 Supabase（queries/security_events）
- [ ] 历史与统计 API（分页、聚合 count/avg/p95/max）
- [ ] 前端联调：提交表单、展示建议、历史列表与统计画像
- [ ] 安全与治理：鉴权（API Key/JWT）、速率限制、CORS 白名单
- [ ] 性能与可观测性：端到端耗时、LLM 分时记录、慢查询分析
- [ ] 数据迁移与回滚：文件落盘 → Supabase；保留降级路径
- [ ] CI/CD：Dev/Preview/Prod 环境与自动发布

## 验收标准（阶段性）
- M1（后端与数据库）
  - POST /api/medical/query 可写入 Supabase，返回结构化 JSON。
  - GET /api/history 可分页返回历史。
  - GET /api/stats 返回聚合：count/avg/p95/max。
- M2（前端）
  - / 页面提交成功并展示建议与候选分析（probabilities、best_candidate）。
  - /history 展示列表与详情，支持刷新与删除。
  - /stats 展示统计与画像（年龄段概率聚合）。
- M3（安全与性能）
  - 非授权请求被拒绝；速率限制生效；跨域仅允许可信来源。
  - 端到端耗时与 LLM 分时入库；统计页指标正确。

## 截断验收标准与自测
- 服务端返回 JSON 必须可解析（不含 Markdown 包裹或截断）。
- 字段完整性：`status`、`advice`、`supplementary_info.probabilities`、`best_candidate`、`total_duration_ms`。
- 自测步骤：
  - 使用 3 组输入（正常、非医疗、恶意），确保状态分别为 success/no_match/failed。
  - 历史写入后，统计页 `count/avg/p95/max` 指标与样本一致。
  - 随机 10 次请求，验证 JSON 解析 100% 成功率。
  - 本地脚本：`conda run -n llm_pro python v2/tests/acceptance_local.py`（不依赖外部密钥，走 fallback）。
  - 连通性检查：`conda run -n llm_pro python v2/tests/ping_supabase.py`（建表后预期 200）。

## 环境与变量
- 前端：`NEXT_PUBLIC_API_BASE`
- 后端：`DEEPSEEK_API_KEY`、`DEEPSEEK_API_URL`、`DEEPSEEK_MODEL`、`TEMPERATURE`、`MAX_TOKENS`、`SUPABASE_URL`、`SUPABASE_SERVICE_ROLE_KEY`

## 风险与回滚
- Supabase 不可用时，回退为文件写入模式；统计切换为近似计算。
- 前端不可用时，保留 Streamlit 临时入口。

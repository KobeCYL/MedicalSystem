"""Streamlit前端界面 - 医疗导诊系统"""
import streamlit as st
import requests
import json
import os
from typing import List, Dict
from datetime import datetime

# 页面配置
st.set_page_config(
    page_title="智能医疗导诊系统",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 样式设置
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# 标题
st.markdown('<h1 class="main-header">🤖 智能医疗导诊系统</h1>', unsafe_allow_html=True)

def _history_path() -> str:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    logs_path = os.path.join(project_root, "logs", "query_history.json")
    root_path = os.path.join(project_root, "query_history.json")
    if os.path.exists(logs_path):
        return logs_path
    if os.path.exists(root_path):
        return root_path
    return logs_path

def _read_file_history() -> List[Dict]:
    path = _history_path()
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            obj = json.load(f)
            return obj if isinstance(obj, list) else []
    except Exception:
        # 解析失败时，不返回空，保持现有会话数据，避免覆盖为0
        return st.session_state.get('query_history', [])

def _write_file_history(data: List[Dict]):
    path = _history_path()
    tmp_path = path + ".tmp"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp_path, path)
    except Exception:
        pass

def _load_history_into_session():
    file_history = _read_file_history()
    if file_history:
        st.session_state.query_history = file_history
    elif 'query_history' not in st.session_state:
        st.session_state.query_history = []

_load_history_into_session()

# 侧边栏配置
with st.sidebar:
    st.header("⚙️ 系统配置")
    api_url = st.text_input(
        "API地址",
        value="http://localhost:5000",
        help="后端服务API地址"
    )
    
    st.header("📊 系统信息")
    if st.button("检查服务状态"):
        try:
            response = requests.get(f"{api_url}/health", timeout=5)
            if response.status_code == 200:
                st.success("✅ 服务正常运行")
            else:
                st.error("❌ 服务异常")
        except:
            st.error("❌ 无法连接到服务")
    
    st.header("📖 使用说明")
    st.info("""
    1. 描述您的症状
    2. 填写患者信息
    3. 点击获取建议
    4. 查看AI生成的医疗建议
    """)

# 主界面
tab1, tab2, tab3, tab4 = st.tabs(["🔍 症状查询", "📋 查询历史", "🔒 恶意统计", "📈 人群画像"])

with tab1:
    with st.form("medical_query_form", clear_on_submit=False):
        col1, col2 = st.columns([2, 1])
        with col1:
            symptom = st.text_area(
                "请描述您的症状:",
                placeholder="例如：头痛、发烧、咳嗽、流鼻涕...",
                height=100,
                help="请详细描述您的症状，包括持续时间、严重程度等"
            )
        with col2:
            st.markdown("**💡 提示**")
            st.caption("• 描述要具体")
            st.caption("• 包含主要症状")
            st.caption("• 注明持续时间")
        st.subheader("👤 患者信息")
        patient_col1, patient_col2, patient_col3 = st.columns(3)
        with patient_col1:
            age = st.number_input("年龄", min_value=0, max_value=120, value=25, help="患者年龄")
        with patient_col2:
            gender = st.selectbox("性别", ["男", "女", "其他"], help="患者性别")
        with patient_col3:
            special_conditions = st.text_input("特殊状况（可选）", placeholder="如怀孕、慢性病、过敏史等", help="任何需要特别说明的健康状况")
        submitted = st.form_submit_button("🚀 获取医疗建议", use_container_width=True)
        if submitted:
            if symptom.strip():
                payload = {
                    "symptom": symptom,
                    "patient_info": {
                        "age": age,
                        "gender": gender,
                        "special_conditions": special_conditions
                    },
                    "client_start_ts": datetime.now().isoformat()
                }
                with st.spinner("🔍 正在分析症状并生成建议..."):
                    try:
                        response = None
                        for attempt in range(2):
                            try:
                                response = requests.post(f"{api_url}/api/medical/query", json=payload, timeout=30)
                                break
                            except requests.exceptions.RequestException:
                                if attempt == 0:
                                    continue
                                raise
                        if response and response.status_code == 200:
                            result = response.json()
                            if 'query_history' not in st.session_state:
                                st.session_state.query_history = []
                            st.session_state.query_history.append({
                                'timestamp': datetime.now().isoformat(),
                                'symptom': symptom,
                                'result': result
                            })
                            if result['status'] == 'success':
                                st.markdown("<div class='success-box'>", unsafe_allow_html=True)
                                st.success(f"**诊断结果**: {result['disease_name']}")
                                urgency_color = {"高": "🔴", "中": "🟡", "低": "🟢", "未知": "⚪"}
                                st.info(f"**紧急程度**: {urgency_color.get(result.get('urgency', '未知'), '⚪')} {result.get('urgency', '未知')}")
                                advice_data = {}
                                try:
                                    advice_data = json.loads(result.get('advice', '{}')) if isinstance(result.get('advice'), str) else (result.get('advice') or {})
                                except Exception:
                                    advice_data = {}
                                st.subheader("建议与处理")
                                st.write(advice_data.get('assessment', ''))
                                actions = advice_data.get('immediate_actions', [])
                                if actions:
                                    st.markdown("**立即行动**")
                                    for a in actions:
                                        st.write(f"- {a}")
                                st.markdown("**医疗建议**")
                                st.write(advice_data.get('medical_advice', ''))
                                points = advice_data.get('monitoring_points', [])
                                if points:
                                    st.markdown("**监测要点**")
                                    for p in points:
                                        st.write(f"- {p}")
                                if advice_data.get('emergency_handling'):
                                    st.markdown("**紧急处理**")
                                    st.write(advice_data.get('emergency_handling'))
                                supp = result.get('supplementary_info') or {}
                                multi = supp.get('multi_analysis') or {}
                                probs = multi.get('probabilities') or []
                                if probs:
                                    st.subheader("候选疾病概率分布")
                                    id_name = {c.get('disease_id'): c.get('disease_name') for c in (supp.get('candidates') or [])}
                                    for pr in probs:
                                        name = pr.get('disease_name') or id_name.get(pr.get('disease_id')) or pr.get('disease_id')
                                        st.write(f"- {name}: {pr.get('probability')}%")
                                    if multi.get('advice'):
                                        st.subheader("综合建议")
                                        st.write(multi.get('advice'))
                                    if multi.get('notes'):
                                        st.subheader("综合注意事项")
                                        st.write(multi.get('notes'))
                                best = multi.get('best_candidate')
                                if best:
                                    st.subheader("最大概率病情")
                                    st.write(f"{best.get('disease_name')}（{best.get('probability')}%）")
                                    bg = best.get('guideline') or {}
                                    br = best.get('risk') or {}
                                    st.markdown("**该病情的建议措施**")
                                    st.write(bg.get('recommended_action', '建议就医'))
                                    st.markdown("**该病情的注意事项**")
                                    st.write(br.get('special_notes', '暂无'))
                                st.markdown("</div>", unsafe_allow_html=True)
                            elif result['status'] == 'no_match':
                                st.markdown("<div class='warning-box'>", unsafe_allow_html=True)
                                st.warning(result['error_message'])
                                st.info("💡 请尝试更详细地描述症状，例如：头痛的位置、持续时间、伴随症状等")
                                st.markdown("</div>", unsafe_allow_html=True)
                            else:
                                st.markdown("<div class='error-box'>", unsafe_allow_html=True)
                                st.error(result['error_message'])
                                st.markdown("</div>", unsafe_allow_html=True)
                        else:
                            st.error(f"请求失败: HTTP {response.status_code}")
                    except requests.exceptions.Timeout:
                        st.error("⏰ 请求超时，请检查服务是否正常运行")
                    except requests.exceptions.ConnectionError:
                        st.error("🔌 无法连接到服务，请检查API地址是否正确")
                    except Exception as e:
                        st.error(f"❌ 系统错误: {e}")
            else:
                st.warning("⚠️ 请输入症状描述")

with tab2:
    st.subheader("📋 查询历史")
    if st.button("🔄 刷新本地历史", key="refresh_history"):
        file_history = _read_file_history()
        st.session_state.query_history = file_history
        st.success(f"已刷新，共 {len(st.session_state.query_history)} 条记录")
    if st.button("🔄 从服务刷新历史", key="refresh_service_history"):
        try:
            resp = requests.get(f"{api_url}/api/history", timeout=8)
            if resp.status_code == 200:
                data = resp.json()
                st.session_state.query_history = data if isinstance(data, list) else []
                st.success(f"已从服务刷新，共 {len(st.session_state.query_history)} 条记录")
            else:
                st.error("服务历史获取失败")
        except Exception:
            st.error("无法连接到服务")
    if not st.session_state.query_history:
        st.info("暂无查询历史")
    else:
        for i, history in enumerate(reversed(st.session_state.query_history)):
            with st.expander(f"查询 {len(st.session_state.query_history) - i}: {history['symptom'][:50]}..."):
                st.write(f"**时间**: {datetime.fromisoformat(history['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}")
                st.write(f"**症状**: {history['symptom']}")
                dur = history.get('duration_ms') or history.get('server_duration_ms')
                if isinstance(dur, (int, float)):
                    st.write(f"**服务耗时**: {int(dur)} ms")
                tot = history.get('total_duration_ms')
                if isinstance(tot, (int, float)):
                    st.write(f"**总耗时**: {int(tot)} ms")
                if history['result']['status'] == 'success':
                    st.success(f"诊断: {history['result']['disease_name']}")
                    st.info(f"紧急程度: {history['result']['urgency']}")
                    advice_data = {}
                    try:
                        advice_data = json.loads(history['result'].get('advice', '{}')) if isinstance(history['result'].get('advice'), str) else (history['result'].get('advice') or {})
                    except Exception:
                        advice_data = {}
                    st.subheader("建议与处理")
                    st.write(advice_data.get('assessment', ''))
                    actions = advice_data.get('immediate_actions', [])
                    if actions:
                        st.markdown("**立即行动**")
                        for a in actions:
                            st.write(f"- {a}")
                    st.markdown("**医疗建议**")
                    st.write(advice_data.get('medical_advice', ''))
                    points = advice_data.get('monitoring_points', [])
                    if points:
                        st.markdown("**监测要点**")
                        for p in points:
                            st.write(f"- {p}")
                    if advice_data.get('emergency_handling'):
                        st.markdown("**紧急处理**")
                        st.write(advice_data.get('emergency_handling'))
                    supp = history['result'].get('supplementary_info') or {}
                    multi = supp.get('multi_analysis') or {}
                    probs = multi.get('probabilities') or []
                    if probs:
                        st.subheader("候选疾病概率分布")
                        id_name = {c.get('disease_id'): c.get('disease_name') for c in (supp.get('candidates') or [])}
                        for pr in probs:
                            name = pr.get('disease_name') or id_name.get(pr.get('disease_id')) or pr.get('disease_id')
                            st.write(f"- {name}: {pr.get('probability')}%")
                        if multi.get('advice'):
                            st.subheader("综合建议")
                            st.write(multi.get('advice'))
                        if multi.get('notes'):
                            st.subheader("综合注意事项")
                            st.write(multi.get('notes'))
                    best = multi.get('best_candidate')
                    if best:
                        st.subheader("最大概率病情")
                        st.write(f"{best.get('disease_name')}（{best.get('probability')}%）")
                        bg = best.get('guideline') or {}
                        br = best.get('risk') or {}
                        st.markdown("**该病情的建议措施**")
                        st.write(bg.get('recommended_action', '建议就医'))
                        st.markdown("**该病情的注意事项**")
                        st.write(br.get('special_notes', '暂无'))
                else:
                    st.error(history['result']['error_message'])
                if st.button(f"删除", key=f"delete_{i}"):
                    st.session_state.query_history.pop(len(st.session_state.query_history) - 1 - i)
                    st.success("已删除，刷新以同步本地文件")
                    _write_file_history(st.session_state.query_history)

with tab3:
    st.subheader("🔒 恶意与正常统计")
    hist = st.session_state.get('query_history', [])
    malicious = 0
    normal = 0
    non_medical = 0
    for h in hist:
        res = h.get('result', {})
        status = res.get('status')
        msg = res.get('error_message') or ""
        if status == 'success':
            normal += 1
        elif status == 'no_match':
            non_medical += 1
        else:
            malicious += 1
    colm1, colm2, colm3 = st.columns(3)
    colm1.metric("正常次数", normal)
    colm2.metric("恶意/不合规次数", malicious)
    colm3.metric("非医疗表达次数", non_medical)
    try:
        stats_resp = requests.get(f"{api_url}/api/stats", timeout=8)
        if stats_resp.status_code == 200:
            stats = stats_resp.json()
            d = stats.get('durations_ms', {})
            st.subheader("⏱️ 性能统计")
            st.write({
                "样本数": d.get('count', 0),
                "平均耗时ms": d.get('avg', 0.0),
                "P95耗时ms": d.get('p95', 0.0),
                "最大耗时ms": d.get('max', 0.0)
            })
    except Exception:
        pass
    if malicious > 0:
        st.subheader("恶意样例")
        for h in hist:
            res = h.get('result', {})
            if res.get('status') == 'failed':
                st.write({"time": h.get('timestamp'), "symptom": h.get('symptom')[:60], "reason": res.get('error_message')})

with tab4:
    st.subheader("📈 年龄与疾病概率分布")
    hist = st.session_state.get('query_history', [])
    def age_group(age):
        try:
            a = int(age)
        except Exception:
            return "未知"
        if a < 13:
            return "0-12"
        if a < 18:
            return "13-17"
        if a < 40:
            return "18-39"
        if a < 65:
            return "40-64"
        return "65+"
    agg = {}
    for h in hist:
        res = h.get('result', {})
        if res.get('status') != 'success':
            continue
        age = h.get('patient_info', {}).get('age')
        grp = age_group(age)
        supp = res.get('supplementary_info') or {}
        multi = supp.get('multi_analysis') or {}
        probs = multi.get('probabilities') or []
        for pr in probs:
            name = pr.get('disease_name') or pr.get('disease_id')
            prob = pr.get('probability') or 0
            key = (grp, name)
            if key not in agg:
                agg[key] = {"age_group": grp, "disease": name, "sum_prob": 0, "count": 0}
            agg[key]["sum_prob"] += prob
            agg[key]["count"] += 1
    rows = []
    for v in agg.values():
        mean = v["sum_prob"] / v["count"] if v["count"] else 0
        rows.append({"年龄段": v["age_group"], "疾病": v["disease"], "样本数": v["count"], "平均概率%": round(mean, 1)})
    if rows:
        rows = sorted(rows, key=lambda x: (x["年龄段"], -x["平均概率%"]))
        st.table(rows)
    else:
        st.info("暂无可统计的数据")

# 页脚
st.markdown("---")
st.caption("⚠️ 免责声明: 本系统提供的建议仅供参考，不能替代专业医疗诊断。如有紧急情况请立即就医。")
st.caption("© 2024 智能医疗导诊系统 | 版本 1.0.0")

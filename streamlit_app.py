"""Streamlit前端界面 - 医疗导诊系统"""
import streamlit as st
import requests
import json
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
tab1, tab2 = st.tabs(["🔍 症状查询", "📋 查询历史"])

with tab1:
    # 症状输入
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
    
    # 患者信息
    st.subheader("👤 患者信息")
    patient_col1, patient_col2, patient_col3 = st.columns(3)
    
    with patient_col1:
        age = st.number_input(
            "年龄",
            min_value=0,
            max_value=120,
            value=25,
            help="患者年龄"
        )
    
    with patient_col2:
        gender = st.selectbox(
            "性别",
            ["男", "女", "其他"],
            help="患者性别"
        )
    
    with patient_col3:
        special_conditions = st.text_input(
            "特殊状况（可选）",
            placeholder="如怀孕、慢性病、过敏史等",
            help="任何需要特别说明的健康状况"
        )
    
    # 查询按钮
    if st.button("🚀 获取医疗建议", type="primary", use_container_width=True):
        if symptom.strip():
            # 准备请求数据
            payload = {
                "symptom": symptom,
                "patient_info": {
                    "age": age,
                    "gender": gender,
                    "special_conditions": special_conditions
                }
            }
            
            # 显示加载状态
            with st.spinner("🔍 正在分析症状并生成建议..."):
                try:
                    response = requests.post(
                        f"{api_url}/api/medical/query",
                        json=payload,
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        # 保存查询历史
                        if 'query_history' not in st.session_state:
                            st.session_state.query_history = []
                        
                        st.session_state.query_history.append({
                            'timestamp': datetime.now().isoformat(),
                            'symptom': symptom,
                            'result': result
                        })
                        
                        # 显示结果
                        if result['status'] == 'success':
                            st.markdown("<div class='success-box'>", unsafe_allow_html=True)
                            st.success(f"**诊断结果**: {result['disease_name']}")
                            
                            # 紧急程度显示
                            urgency_color = {
                                "高": "🔴",
                                "中": "🟡", 
                                "低": "🟢",
                                "未知": "⚪"
                            }
                            st.info(f"**紧急程度**: {urgency_color.get(result['urgency'], '⚪')} {result['urgency']}")
                            
                            # 显示建议
                            st.write(f"**建议**:")
                            st.write(result['advice'])
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
    
    if 'query_history' not in st.session_state or not st.session_state.query_history:
        st.info("暂无查询历史")
    else:
        for i, history in enumerate(reversed(st.session_state.query_history)):
            with st.expander(f"查询 {len(st.session_state.query_history) - i}: {history['symptom'][:50]}..."):
                st.write(f"**时间**: {datetime.fromisoformat(history['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}")
                st.write(f"**症状**: {history['symptom']}")
                
                if history['result']['status'] == 'success':
                    st.success(f"诊断: {history['result']['disease_name']}")
                    st.info(f"紧急程度: {history['result']['urgency']}")
                    st.write(f"建议: {history['result']['advice']}")
                else:
                    st.error(history['result']['error_message'])
                
                # 删除按钮
                if st.button(f"删除", key=f"delete_{i}"):
                    st.session_state.query_history.pop(len(st.session_state.query_history) - 1 - i)
                    st.rerun()

# 页脚
st.markdown("---")
st.caption("⚠️ 免责声明: 本系统提供的建议仅供参考，不能替代专业医疗诊断。如有紧急情况请立即就医。")
st.caption("© 2024 智能医疗导诊系统 | 版本 1.0.0")
"""
A/B测试样本量计算器 - Streamlit应用
用于精确计算A/B测试所需的样本量
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from SampleCalculator import SampleSizeCalculator
import math

# 页面配置
st.set_page_config(
    page_title="样本量计算器 - A/B测试工具",
    page_icon="🧮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化session_state
if 'baseline_from_file' not in st.session_state:
    st.session_state.baseline_from_file = None
if 'variance_from_file' not in st.session_state:
    st.session_state.variance_from_file = None

# 自定义CSS样式
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #667eea;
        padding: 20px 0;
    }
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 12px 24px;
        font-weight: 600;
        width: 100%;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin: 10px 0;
    }
    /* 确保number_input的spinner按钮显示 */
    .stNumberInput > div > div > button {
        display: flex !important;
        visibility: visible !important;
    }
    /* 确保输入框布局正确 */
    .stNumberInput {
        width: 100%;
    }
    /* 强制显示spinner按钮（增加和减少按钮） */
    button[data-testid="stNumberInputStepUp"],
    button[data-testid="stNumberInputStepDown"],
    button[data-testid*="StepUp"],
    button[data-testid*="StepDown"] {
        display: inline-flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        pointer-events: auto !important;
    }
    /* 确保spinner按钮容器可见 */
    div[data-baseweb="input"] button,
    .stNumberInput button,
    [data-baseweb="input"] button {
        display: inline-flex !important;
        visibility: visible !important;
        opacity: 1 !important;
    }
    /* 确保number input的suffix区域显示 */
    [data-baseweb="input"] > div:last-child,
    .stNumberInput > div > div:last-child {
        display: flex !important;
        visibility: visible !important;
    }
</style>
""", unsafe_allow_html=True)

# 标题
st.markdown('<h1 class="main-header">🧮 样本量计算器</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #666; margin-bottom: 30px;">精确计算A/B测试所需的样本量</p>', unsafe_allow_html=True)

# 侧边栏 - 参数设置
with st.sidebar:
    st.header("⚙️ 参数设置")
    st.caption("配置实验参数以计算所需样本量")
    
    # 数据文件上传
    st.subheader("数据文件（可选）")
    uploaded_file = st.file_uploader(
        "上传CSV文件自动计算基准值和方差",
        type=['csv'],
        help="上传CSV文件，系统将自动计算第一列数据的均值和方差作为基准值和方差"
    )
    
    # 如果上传了文件，处理数据
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            if len(df) > 0:
                # 获取第一列数据
                first_column = df.columns[0]
                values = pd.to_numeric(df[first_column], errors='coerce').dropna()
                
                if len(values) > 0:
                    st.session_state.baseline_from_file = values.mean()
                    st.session_state.variance_from_file = values.var(ddof=1)
                    st.success(f"✅ 成功读取文件: {uploaded_file.name}")
                    st.info(f"基准值: {st.session_state.baseline_from_file:.6f}\n方差: {st.session_state.variance_from_file:.6f}")
                else:
                    st.error("无法从CSV文件中提取数值数据")
                    st.session_state.baseline_from_file = None
                    st.session_state.variance_from_file = None
        except Exception as e:
            st.error(f"文件读取失败: {str(e)}")
            st.session_state.baseline_from_file = None
            st.session_state.variance_from_file = None
    else:
        # 如果没有上传文件，清除之前的值
        st.session_state.baseline_from_file = None
        st.session_state.variance_from_file = None
    
    st.divider()
    
    # 指标类型
    metric_type = st.selectbox(
        "指标类型",
        ["比例", "均值"],
        help="选择指标类型：比例（如转化率）或均值（如平均收入）"
    )
    
    # 基准值
    if st.session_state.baseline_from_file is not None:
        baseline_value = st.number_input(
            "基准值 *",
            min_value=0.0,
            value=st.session_state.baseline_from_file,
            step=0.001,
            format="%.6f",
            help="对照组的预期指标值（已从CSV文件自动填充）",
            key="baseline_input"
        )
    else:
        baseline_value = st.number_input(
            "基准值 *",
            min_value=0.0,
            value=0.06,
            step=0.001,
            format="%.6f",
            help="对照组的预期指标值",
            key="baseline_input"
        )
    
    # 方差
    if st.session_state.variance_from_file is not None:
        variance = st.number_input(
            "方差 *",
            min_value=0.0,
            value=st.session_state.variance_from_file,
            step=0.001,
            format="%.6f",
            help="指标的方差值（已从CSV文件自动填充）",
            key="variance_input"
        )
    else:
        variance = st.number_input(
            "方差 *",
            min_value=0.0,
            value=0.05,
            step=0.001,
            format="%.6f",
            help="指标的方差值",
            key="variance_input"
        )
    
    st.divider()
    
    # MDE参数
    st.subheader("MDE参数")
    
    mde_start = st.number_input(
        "MDE开始值 *",
        min_value=0.0,
        value=0.001,
        step=0.001,
        format="%.6f",
        help="最小可检测效应的起始值（如：0.001表示0.1%）",
        key="mde_start_input"
    )
    
    mde_end = st.number_input(
        "MDE结束值 *",
        min_value=0.0,
        value=0.01,
        step=0.01,
        format="%.6f",
        help="最小可检测效应的结束值（如：0.01表示1%）",
        key="mde_end_input"
    )
    
    mde_step = st.number_input(
        "MDE步长 *",
        min_value=0.0,
        value=0.001,
        step=0.001,
        format="%.6f",
        help="MDE值的递增步长（如：0.001表示每次增加0.1%）",
        key="mde_step_input"
    )
    
    st.divider()
    
    # 实验组参数
    st.subheader("实验组参数")
    
    k_value = st.number_input(
        "K值",
        min_value=0.1,
        value=1.0,
        step=0.1,
        format="%.1f",
        help="实验组与对照组的流量比例（默认1:1）",
        key="k_value_input"
    )
    
    group_num = st.number_input(
        "实验组数量（不包括对照组）",
        min_value=1,
        value=2,
        step=1,
        help="实验组的数量，不包括对照组",
        key="group_num_input"
    )
    
    total_groups = 1 + group_num
    st.info(f"将创建 1 个对照组 + {group_num} 个实验组 = {total_groups} 个组别")
    
    st.divider()
    
    # 流量参数
    st.subheader("流量参数")
    
    daily_traffic = st.number_input(
        "日活流量",
        min_value=1,
        value=10000,
        step=1,
        help="每日活跃用户数量",
        key="daily_traffic_input"
    )
    
    traffic_ratio = st.number_input(
        "实验流量比例",
        min_value=0.0,
        max_value=1.0,
        value=0.5,
        step=0.1,
        format="%.1f",
        help="参与实验的流量占总流量的比例（0-1之间）",
        key="traffic_ratio_input"
    )
    
    st.divider()
    
    # 统计参数
    st.subheader("统计参数")
    
    significance_level = st.number_input(
        "显著性水平（α）",
        min_value=0.0,
        max_value=1.0,
        value=0.05,
        step=0.01,
        format="%.2f",
        help="第一类错误率，通常为0.05（5%）",
        key="significance_level_input"
    )
    
    power = st.number_input(
        "统计功效（1-β）",
        min_value=0.0,
        max_value=1.0,
        value=0.8,
        step=0.1,
        format="%.1f",
        help="检测到真实效应的概率，通常为0.8（80%）",
        key="power_input"
    )
    
    st.divider()
    
    # 计算按钮
    calculate_button = st.button("计算样本量", type="primary", use_container_width=True)

# 主内容区
if calculate_button:
    # 验证参数
    if mde_start >= mde_end:
        st.error("❌ MDE开始值必须小于MDE结束值")
        st.stop()
    
    if mde_step <= 0:
        st.error("❌ MDE步长必须大于0")
        st.stop()
    
    # 生成MDE序列
    mde_array = np.arange(mde_start, mde_end + mde_step, mde_step)
    mde_array = np.round(mde_array, 6)
    
    # 初始化计算器
    calculator = SampleSizeCalculator(
        significance_level=significance_level,
        power=power
    )
    
    # 计算结果
    results = []
    
    with st.spinner("正在计算样本量..."):
        for mde in mde_array:
            if metric_type == "比例":
                control_sample = calculator.calculate_binary_metric_sample_size(
                    baseline_value, mde, k_value
                )
            else:  # 均值
                # 使用基准值和方差直接计算
                control_sample = calculator.calculate_continuous_metric_sample_size_from_params(
                    baseline_value, variance, mde, k_value
                )
            
            treatment_sample = math.ceil(control_sample * k_value)
            total_sample = control_sample + treatment_sample * group_num
            experiment_days = math.ceil(total_sample / (daily_traffic * traffic_ratio))
            
            results.append({
                'MDE': f"{mde * 100:.2f}%",
                'MDE值': mde,
                '对照组': control_sample,
                '每组实验组': treatment_sample,
                '总样本': total_sample,
                '实验天数': experiment_days
            })
    
    # 转换为DataFrame
    results_df = pd.DataFrame(results)
    
    # 显示结果信息
    st.success(f"✅ 计算完成！实验组数量: {group_num} (1个对照组 + {group_num}个实验组 = {total_groups}个组别)")
    
    # 结果表格
    st.subheader("📊 计算结果表")
    
    # 格式化显示
    display_df = results_df.copy()
    display_df['对照组'] = display_df['对照组'].apply(lambda x: f"{x:,}")
    display_df['每组实验组'] = display_df['每组实验组'].apply(lambda x: f"{x:,}")
    display_df['总样本'] = display_df['总样本'].apply(lambda x: f"{x:,}")
    display_df['实验天数'] = display_df['实验天数'].apply(lambda x: f"{x:,}")
    
    st.dataframe(
        display_df[['MDE', '对照组', '每组实验组', '总样本', '实验天数']],
        use_container_width=True,
        hide_index=True
    )
    
    # 导出按钮
    csv = results_df[['MDE值', '对照组', '每组实验组', '总样本', '实验天数']].to_csv(index=False)
    st.download_button(
        label="📥 导出结果",
        data=csv,
        file_name=f"样本量计算结果_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )
    
    # 样本量趋势图
    st.subheader("📈 样本量趋势图")
    
    fig = px.line(
        results_df,
        x='MDE',
        y='总样本',
        markers=True,
        title='MDE vs 总样本量',
        labels={'MDE': 'MDE (%)', '总样本': '总样本量'}
    )
    
    fig.update_traces(
        line=dict(color='#667eea', width=3),
        marker=dict(size=6, color='#667eea')
    )
    
    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family="PingFang SC, Microsoft YaHei, sans-serif"),
        xaxis=dict(gridcolor='rgba(0,0,0,0.05)'),
        yaxis=dict(gridcolor='rgba(0,0,0,0.05)'),
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
else:
    # 初始状态显示
    st.info("👆 请在左侧边栏配置参数，然后点击「计算样本量」按钮开始计算")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>📊 参数设置</h3>
            <p>配置实验参数以计算所需样本量</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>📈 结果展示</h3>
            <p>查看计算结果表和趋势图</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>💾 数据导出</h3>
            <p>导出计算结果为CSV文件</p>
        </div>
        """, unsafe_allow_html=True)


# A/B测试样本量计算器

一个用于精确计算A/B测试所需样本量的Web应用，支持Streamlit部署。

## 功能特性

- 📊 **参数设置**：支持配置实验参数以计算所需样本量
- 📁 **CSV文件上传**：上传CSV文件自动计算基准值和方差
- 📈 **结果展示**：显示计算结果表和趋势图
- 💾 **数据导出**：导出计算结果为CSV文件
- 🎯 **多种指标类型**：支持比例和均值两种指标类型

## 安装和运行

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行应用

```bash
streamlit run main.py
```

应用将在浏览器中自动打开，默认地址为 `http://localhost:8501`

## 部署到Streamlit Cloud

1. 将代码推送到GitHub仓库
2. 访问 [Streamlit Cloud](https://streamlit.io/cloud)
3. 点击 "New app"
4. 选择你的GitHub仓库和分支
5. 设置主文件路径为 `main.py`
6. 点击 "Deploy"

## 项目结构

```
streamlit_app/
├── main.py              # Streamlit主应用文件（用于部署）
├── SampleCalculator.py  # 样本量计算核心逻辑
├── requirements.txt     # Python依赖包
├── README.md           # 项目说明文档
└── DEPLOYMENT.md       # 部署指南
```

## 使用说明

### 参数设置

1. **数据文件（可选）**：上传CSV文件，系统将自动计算第一列数据的均值和方差
2. **指标类型**：选择"比例"或"均值"
3. **基准值**：对照组的预期指标值
4. **方差**：指标的方差值
5. **MDE参数**：设置MDE开始值、结束值和步长
6. **实验组参数**：设置K值和实验组数量
7. **流量参数**：设置日活流量和实验流量比例
8. **统计参数**：设置显著性水平和统计功效

### 计算结果

点击"计算样本量"按钮后，将显示：
- 计算结果表：包含MDE、对照组、每组实验组、总样本、实验天数
- 样本量趋势图：展示MDE与总样本量的关系
- 导出功能：可将结果导出为CSV文件

## 技术栈

- **Streamlit**：Web应用框架
- **Pandas**：数据处理
- **NumPy**：数值计算
- **SciPy**：统计计算
- **Plotly**：数据可视化

## 作者

3-David 的计算器项目作业

## 许可证

MIT License


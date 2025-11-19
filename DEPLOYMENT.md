# 部署指南

## 本地运行

1. **安装依赖**
```bash
cd streamlit_app
pip install -r requirements.txt
```

2. **运行应用**
```bash
streamlit run main.py
```

应用将在浏览器中自动打开，默认地址为 `http://localhost:8501`

## 部署到GitHub

1. **初始化Git仓库**（如果还没有）
```bash
cd streamlit_app
git init
```

2. **添加文件**
```bash
git add .
git commit -m "Initial commit: A/B测试样本量计算器"
```

3. **创建GitHub仓库并推送**
   - 在GitHub上创建一个新仓库
   - 添加远程仓库地址
```bash
git remote add origin https://github.com/yourusername/your-repo-name.git
git branch -M main
git push -u origin main
```

## 部署到Streamlit Cloud

1. **访问Streamlit Cloud**
   - 访问 https://streamlit.io/cloud
   - 使用GitHub账号登录

2. **创建新应用**
   - 点击 "New app"
   - 选择你的GitHub仓库
   - 选择分支（通常是 `main`）
   - 设置主文件路径为 `main.py`

3. **部署**
   - 点击 "Deploy"
   - 等待部署完成
   - 应用将自动生成一个公开URL

## 文件结构说明

```
streamlit_app/
├── main.py              # Streamlit主应用文件（必需，用于部署）
├── SampleCalculator.py  # 样本量计算核心逻辑（必需）
├── requirements.txt     # Python依赖包（必需）
├── README.md           # 项目说明文档
└── DEPLOYMENT.md       # 部署指南（本文件）
```

## 注意事项

1. **requirements.txt** 必须包含所有依赖包
2. **main.py** 必须是主应用文件
3. 确保所有Python文件使用UTF-8编码
4. 如果使用中文，确保文件编码正确

## 故障排除

### 问题：导入错误
- 确保 `SampleCalculator.py` 在同一目录下
- 检查 `requirements.txt` 中的包版本

### 问题：CSV文件上传失败
- 确保CSV文件格式正确
- 检查文件编码（建议使用UTF-8）

### 问题：计算结果不正确
- 检查参数设置是否正确
- 确保MDE开始值小于结束值
- 验证基准值和方差的合理性


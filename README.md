# 文献解读 PubMed 版

为临床医生提供结构化文献解读的AI工具。

## 功能特点

- 🔍 自动搜索PubMed文献
- 📊 生成7维度结构化解读
- 🎯 临床医生视角
- 🇨🇳 中文输出

## 解读维度

1. **研究类型** - RCT/Meta-analysis/Cohort等
2. **样本量** - n=XXXX
3. **研究问题** - 一句话说明
4. **核心结论** - 2-3条要点
5. **研究提示** - 局限性/注意事项
6. **临床意义** - 实践价值
7. **适用人群** - 特定人群

## 使用方法

1. 输入医学问题
2. 系统自动搜索PubMed
3. AI生成结构化解读

## 技术栈

- 前端：Streamlit
- 数据源：PubMed E-utilities API
- AI：DeepSeek

## 本地运行

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 环境变量

```bash
export DEEPSEEK_API_KEY="your-api-key"
```

## 注意事项

⚠️ 本工具仅供参考，不构成医疗建议

## 作者

二月 & 小二 🦦

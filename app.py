import streamlit as st
import requests
from openai import OpenAI
import os
import xml.etree.ElementTree as ET

# 页面配置
st.set_page_config(
    page_title="文献解读 PubMed 版",
    page_icon="📚",
    layout="wide"
)

# 标题
st.title("📚 文献解读 PubMed 版")
st.markdown("**为临床医生提供结构化文献解读**")

# 侧边栏配置
with st.sidebar:
    st.header("⚙️ 配置")
    deepseek_api_key = st.text_input(
        "DeepSeek API Key",
        type="password",
        value=os.getenv("DEEPSEEK_API_KEY", "")
    )
    max_results = st.slider("最大文献数量", 1, 10, 5)
    st.markdown("---")
    st.markdown("### 📖 使用说明")
    st.markdown("""
    1. 输入医学问题（中文/英文均可）
    2. 系统自动翻译并搜索PubMed
    3. 生成结构化解读
    
    **解读维度：**
    - 研究类型
    - 样本量
    - 研究问题
    - 核心结论
    - 研究提示
    - 临床意义
    - 适用人群
    """)

def extract_text(element):
    """安全提取XML元素文本"""
    if element is None:
        return ""
    text = element.text or ""
    # 处理子元素
    for child in element:
        if child.text:
            text += child.text
        if child.tail:
            text += child.tail
    return text.strip()

# 主界面
query = st.text_input(
    "🔍 输入医学问题（中文/英文均可）",
    placeholder="例如：SGLT2抑制剂在心血管疾病中的作用"
)

if st.button("🚀 开始解读", type="primary"):
    if not query:
        st.warning("请输入问题")
    elif not deepseek_api_key:
        st.error("请在侧边栏配置 DeepSeek API Key")
    else:
        try:
            # 初始化AI客户端（在这里初始化，确保有API key）
            client = OpenAI(
                api_key=deepseek_api_key,
                base_url="https://api.deepseek.com"
            )
            
            # 1. 翻译问题为英文（如果是中文）
            with st.spinner("正在处理问题..."):
                # 检测是否包含中文
                has_chinese = any('\u4e00' <= char <= '\u9fff' for char in query)
                
                if has_chinese:
                    st.info("🌐 检测到中文问题，正在翻译为英文...")
                    translate_response = client.chat.completions.create(
                        model="deepseek-chat",
                        messages=[
                            {"role": "system", "content": "你是一个医学翻译助手。请将用户的中文医学问题翻译成准确的英文医学术语，用于PubMed搜索。只返回翻译结果，不要解释。"},
                            {"role": "user", "content": f"翻译这个医学问题：{query}"}
                        ],
                        temperature=0.3,
                        max_tokens=200
                    )
                    english_query = translate_response.choices[0].message.content.strip()
                    st.success(f"✅ 翻译结果: {english_query}")
                else:
                    english_query = query
                    st.info(f"🔍 搜索关键词: {english_query}")
            
            # 2. 搜索PubMed
            with st.spinner("正在搜索文献..."):
                search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
                search_params = {
                    "db": "pubmed",
                    "term": english_query,
                    "retmax": max_results,
                    "retmode": "json",
                    "sort": "relevance"
                }
                search_response = requests.get(search_url, params=search_params, timeout=10)
                search_data = search_response.json()
                
                pmids = search_data.get("esearchresult", {}).get("idlist", [])
                
                if not pmids:
                    st.warning("未找到相关文献，请尝试：\n- 使用更通用的医学术语\n- 简化问题描述\n- 使用英文关键词")
                else:
                    st.success(f"找到 {len(pmids)} 篇文献")
                    
                    # 3. 获取文献详情
                    fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
                    fetch_params = {
                        "db": "pubmed",
                        "id": ",".join(pmids),
                        "retmode": "xml"
                    }
                    fetch_response = requests.get(fetch_url, params=fetch_params, timeout=10)
                    
                    # 4. 解析XML
                    root = ET.fromstring(fetch_response.content)
                    
                    articles = []
                    for article in root.findall(".//PubmedArticle"):
                        try:
                            # 安全提取各字段
                            title_elem = article.find(".//ArticleTitle")
                            title = extract_text(title_elem) if title_elem is not None else "无标题"
                            
                            abstract_elem = article.find(".//AbstractText")
                            abstract = extract_text(abstract_elem) if abstract_elem is not None else "无摘要"
                            
                            journal_elem = article.find(".//Journal/Title")
                            journal = extract_text(journal_elem) if journal_elem is not None else "未知期刊"
                            
                            year_elem = article.find(".//PubDate/Year")
                            year = extract_text(year_elem) if year_elem is not None else "未知年份"
                            
                            pmid_elem = article.find(".//PMID")
                            pmid = extract_text(pmid_elem) if pmid_elem is not None else ""
                            
                            # 确保所有字段都是字符串
                            articles.append({
                                "title": str(title),
                                "abstract": str(abstract),
                                "journal": str(journal),
                                "year": str(year),
                                "pmid": str(pmid)
                            })
                        except Exception as e:
                            st.warning(f"解析文献时出错: {str(e)}")
                            continue
                    
                    if not articles:
                        st.error("文献解析失败，请稍后重试")
                    else:
                        # 5. 为每篇文献生成解读
                        for idx, article in enumerate(articles, 1):
                            with st.expander(f"📄 文献 {idx}: {article['title'][:80]}...", expanded=(idx==1)):
                                # 生成解读
                                with st.spinner("正在生成解读..."):
                                    prompt = f"""你是一名医学研究解读助手，请基于以下PubMed文献信息，为临床医生生成结构化解读。

要求：
1. 用中文输出
2. 不要重复原文摘要
3. 用临床医生容易快速阅读的方式总结
4. 内容简洁专业

请按以下结构输出：

【研究类型】
判断研究设计，例如：RCT / Meta-analysis / Cohort / Case-control / Review

【样本量】
如果文献中有样本量，请提取，如 n=XXXX

【研究问题】
一句话说明研究想解决什么问题

【核心结论】
总结研究最重要发现（2-3条）

【研究提示】
指出研究局限或需要注意的地方

【临床意义】
从临床医生角度解释这项研究可能带来的实践意义

【适用人群】
如果研究有特定人群（如糖尿病患者、老年人等）请说明

文献信息如下：
标题：{article['title']}
摘要：{article['abstract']}
期刊：{article['journal']}
年份：{article['year']}
"""
                                    
                                    try:
                                        response = client.chat.completions.create(
                                            model="deepseek-chat",
                                            messages=[
                                                {"role": "system", "content": "你是一名专业的医学研究解读助手。"},
                                                {"role": "user", "content": prompt}
                                            ],
                                            temperature=0.3,
                                            max_tokens=2000
                                        )
                                        
                                        interpretation = response.choices[0].message.content
                                        
                                        # 显示解读
                                        st.markdown("### 📊 结构化解读")
                                        st.markdown(interpretation)
                                        
                                        # 显示原文信息
                                        st.markdown("---")
                                        st.markdown("### 📖 原文信息")
                                        col1, col2 = st.columns(2)
                                        with col1:
                                            st.markdown(f"**期刊：** {article['journal']}")
                                            st.markdown(f"**年份：** {article['year']}")
                                        with col2:
                                            st.markdown(f"**PMID：** {article['pmid']}")
                                            if article['pmid']:
                                                st.markdown(f"[查看原文](https://pubmed.ncbi.nlm.nih.gov/{article['pmid']}/)")
                                        
                                        with st.expander("查看原文摘要"):
                                            st.markdown(article['abstract'])
                                        
                                    except Exception as e:
                                        st.error(f"生成解读失败: {str(e)}")
                        
        except Exception as e:
            st.error(f"发生错误: {str(e)}")
            import traceback
            st.code(traceback.format_exc())

# 页脚
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9em;'>
    <p>数据来源：PubMed | AI解读：DeepSeek</p>
    <p>⚠️ 仅供参考，不构成医疗建议</p>
</div>
""", unsafe_allow_html=True)

import streamlit as st
import requests
import os
import xml.etree.ElementTree as ET
import re

# 页面配置
st.set_page_config(
    page_title="30 秒读懂 PubMed-文献解读助手",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

# 高级学院派CSS样式
st.markdown("""
<style>
    /* 全局字体和行高 */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
    }
    
    body {
        line-height: 1.6em;
    }
    
    /* 主标题样式 */
    h1 {
        font-weight: 600;
        color: #1a1a1a;
        letter-spacing: -0.02em;
        margin-top: 0px;
        margin-bottom: 6px;
    }
    
    /* 搜索框样式 */
    .stTextInput > div > div > input {
        border-radius: 8px;
        border: 1.5px solid #e0e0e0;
        padding: 12px 16px;
        font-size: 0.95rem;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #4A90E2;
        box-shadow: 0 0 0 3px rgba(74, 144, 226, 0.1);
    }
    
    /* 卡片容器样式 */
    .literature-card {
        background: white;
        border-radius: 12px;
        padding: 24px;
        margin: 16px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        border: 1px solid #f0f0f0;
    }
    
    /* 一句话结论高亮 */
    .conclusion-highlight {
        background: linear-gradient(135deg, #E8F5E9 0%, #E3F2FD 100%);
        padding: 16px 20px;
        border-radius: 8px;
        border-left: 4px solid #4CAF50;
        margin: 16px 0;
        font-size: 1.05rem;
        font-weight: 500;
        color: #2c3e50;
        line-height: 1.7;
    }
    
    /* Badge样式 */
    .badge {
        display: inline-block;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin: 4px 6px 4px 0;
        letter-spacing: 0.3px;
    }
    
    .badge-rct {
        background: #FFF3E0;
        color: #E65100;
    }
    
    .badge-meta {
        background: #E3F2FD;
        color: #1565C0;
    }
    
    .badge-cohort {
        background: #E8F5E9;
        color: #2E7D32;
    }
    
    .badge-review {
        background: #F3E5F5;
        color: #6A1B9A;
    }
    
    .badge-high {
        background: #E8F5E9;
        color: #2E7D32;
        border: 1px solid #81C784;
    }
    
    .badge-medium {
        background: #FFF8E1;
        color: #F57C00;
        border: 1px solid #FFB74D;
    }
    
    .badge-low {
        background: #FFEBEE;
        color: #C62828;
        border: 1px solid #E57373;
    }
    
    .badge-top {
        background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
        color: #fff;
        font-weight: 700;
    }
    
    /* 章节标题 */
    .section-header {
        font-size: 0.85rem;
        font-weight: 700;
        color: #5f6368;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-top: 20px;
        margin-bottom: 12px;
        border-bottom: 2px solid #e8eaed;
        padding-bottom: 6px;
    }
    
    /* 内容文本 */
    .content-text {
        color: #3c4043;
        font-size: 0.95rem;
        line-height: 1.7;
        margin-left: 8px;
    }
    
    /* 统计数据高亮 */
    .stat-highlight {
        color: #1565C0;
        font-weight: 700;
    }
    
    /* 原文信息 */
    .meta-info {
        font-size: 0.85rem;
        color: #80868b;
        margin-top: 20px;
        padding-top: 16px;
        border-top: 1px solid #e8eaed;
    }
    
    /* 侧边栏优化 */
    section[data-testid="stSidebar"] {
        background: #fafafa;
    }
    
    section[data-testid="stSidebar"] > div {
        padding-top: 2rem;
    }
    
    /* 按钮优化 */
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        letter-spacing: 0.3px;
        transition: all 0.2s;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    /* Expander优化 */
    .stExpander {
        border: none;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        border-radius: 8px;
        margin: 8px 0;
    }
    
    /* 摘要框 */
    .abstract-box {
        background: #f8f9fa;
        padding: 16px 20px;
        border-radius: 8px;
        border-left: 3px solid #4A90E2;
        margin-top: 12px;
        font-size: 0.9rem;
        line-height: 1.7;
        color: #495057;
    }
</style>
""", unsafe_allow_html=True)

# 标题区域
st.markdown("<h1 style='margin-bottom:6px;'>30 秒读懂 PubMed-文献解读助手</h1>", unsafe_allow_html=True)
st.markdown('<p style="color:#80868b;font-size:0.95rem;margin-top:0px;margin-bottom:10px;">基于 PubMed 搜索，现在你可以输入你的问题</p>', unsafe_allow_html=True)

# 侧边栏配置
with st.sidebar:
    st.markdown("### ⚙️ 配置")
    
    deepseek_api_key = st.text_input(
        "DeepSeek API Key",
        type="password",
        value=os.getenv("DEEPSEEK_API_KEY", ""),
        help="在 https://platform.deepseek.com 获取"
    )
    
    max_results = st.slider("检索文献数量", 1, 10, 5, help="建议5-10篇")
    
    st.markdown("---")
    
    with st.expander("📖 使用说明", expanded=True):
        st.markdown("""
        **功能特点：**
        - 🌐 中英文问题自动翻译
        - 🔍 PubMed权威数据源
        - 📊 7维度临床解读
        - 🏷️ 证据等级标签化
        
        **使用步骤：**
        1. 输入临床问题
        2. 系统自动检索
        3. 查看结构化解读
        4. 切换中英文摘要
        """)
    
    st.markdown("---")
    st.markdown('<p style="font-size: 0.75rem; color: #999;">数据来源：PubMed<br>AI解读：DeepSeek</p>', unsafe_allow_html=True)

# 工具函数
def extract_text(element):
    if element is None:
        return ""
    text = element.text or ""
    for child in element:
        if child.text:
            text += child.text
        if child.tail:
            text += child.tail
    return text.strip()

def call_deepseek(prompt: str, api_key: str) -> str:
    try:
        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": "你是一名专业的医学循证研究助手。"},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3,
                "max_tokens": 2000
            },
            timeout=30
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        raise Exception(f"API调用失败: {str(e)}")

def translate_abstract(abstract: str, api_key: str) -> str:
    try:
        prompt = f"请将以下英文医学摘要翻译成中文，保持专业术语准确：\n\n{abstract}"
        return call_deepseek(prompt, api_key)
    except Exception as e:
        return f"翻译失败: {str(e)}"

def highlight_stats(text: str) -> str:
    """高亮统计数据"""
    # 高亮 HR, OR, RR, P值等
    text = re.sub(r'(HR|OR|RR|P)\s*[=<>]\s*[\d.]+', r'<span class="stat-highlight">\g<0></span>', text, flags=re.IGNORECASE)
    # 高亮百分比
    text = re.sub(r'\d+\.?\d*%', r'<span class="stat-highlight">\g<0></span>', text)
    # 高亮 n=数字
    text = re.sub(r'n\s*=\s*\d+', r'<span class="stat-highlight">\g<0></span>', text, flags=re.IGNORECASE)
    return text

def render_interpretation(interpretation: str):
    """渲染解读内容"""
    lines = interpretation.split("\n")
    current_section = None
    conclusion_text = None
    
    # 第一遍：提取一句话结论
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith("【") and line.endswith("】"):
            section_name = line[1:-1]
            if section_name == "一句话结论":
                current_section = "conclusion"
                continue
        elif current_section == "conclusion":
            conclusion_text = line
            break
    
    # 第二遍：渲染所有内容（跳过一句话结论）
    current_section = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        if line.startswith("【") and line.endswith("】"):
            section_name = line[1:-1]
            
            if section_name == "一句话结论":
                current_section = "skip_conclusion"
                continue
            elif section_name == "证据标签":
                st.markdown(f'<div class="section-header">证据标签</div>', unsafe_allow_html=True)
                current_section = "evidence"
                continue
            else:
                st.markdown(f'<div class="section-header">{section_name}</div>', unsafe_allow_html=True)
                current_section = section_name
        
        elif current_section == "skip_conclusion":
            current_section = None
            continue
        
        elif current_section == "evidence":
            if "研究类型：" in line or "研究类型:" in line:
                content = line.split("：")[-1].split(":")[-1].strip()
                badge_class = "badge"
                if "RCT" in content.upper():
                    badge_class += " badge-rct"
                elif "Meta" in content:
                    badge_class += " badge-meta"
                elif "Cohort" in content or "队列" in content:
                    badge_class += " badge-cohort"
                elif "Review" in content or "综述" in content:
                    badge_class += " badge-review"
                st.markdown(f'<div style="margin: 8px 0;"><strong>研究类型：</strong><span class="{badge_class}">{content}</span></div>', unsafe_allow_html=True)
            
            elif "证据等级：" in line or "证据等级:" in line:
                content = line.split("：")[-1].split(":")[-1].strip()
                badge_class = "badge"
                if "高" in content:
                    badge_class += " badge-high"
                elif "中" in content:
                    badge_class += " badge-medium"
                elif "低" in content:
                    badge_class += " badge-low"
                st.markdown(f'<div style="margin: 8px 0;"><strong>证据等级：</strong><span class="{badge_class}">{content}</span></div>', unsafe_allow_html=True)
            
            elif "样本量：" in line or "样本量:" in line:
                content = line.split("：")[-1].split(":")[-1].strip()
                highlighted = highlight_stats(content)
                st.markdown(f'<div style="margin: 8px 0;"><strong>样本量：</strong>{highlighted}</div>', unsafe_allow_html=True)
            
            elif "期刊级别：" in line or "期刊级别:" in line:
                content = line.split("：")[-1].split(":")[-1].strip()
                badge_class = "badge"
                if "顶级" in content:
                    badge_class += " badge-top"
                st.markdown(f'<div style="margin: 8px 0;"><strong>期刊级别：</strong><span class="{badge_class}">{content}</span></div>', unsafe_allow_html=True)
            
            else:
                highlighted = highlight_stats(line)
                st.markdown(f'<div class="content-text">{highlighted}</div>', unsafe_allow_html=True)
        
        else:
            highlighted = highlight_stats(line)
            st.markdown(f'<div class="content-text">{highlighted}</div>', unsafe_allow_html=True)
    
    return conclusion_text

if 'articles' not in st.session_state:
    st.session_state.articles = []
if 'query_done' not in st.session_state:
    st.session_state.query_done = False
if 'show_abstract' not in st.session_state:
    st.session_state.show_abstract = {}
if 'abstract_lang' not in st.session_state:
    st.session_state.abstract_lang = {}
if 'translated_abstracts' not in st.session_state:
    st.session_state.translated_abstracts = {}

# 主界面 - 搜索区域
col_search, col_btn = st.columns([4, 1])

with col_search:
    query = st.text_input(
        "🔍 输入临床问题",
        placeholder="例如：SGLT2抑制剂在慢性肾病中的疗效",
        label_visibility="collapsed",
        key="query_input"
    )

with col_btn:
    search_button = st.button("🚀 开始检索", type="primary", use_container_width=True)

if search_button:
    if not query:
        st.warning("⚠️ 请输入临床问题")
    elif not deepseek_api_key:
        st.error("❌ 请在侧边栏配置 DeepSeek API Key")
    else:
        # 清空之前的结果
        st.session_state.articles = []
        st.session_state.query_done = False
        st.session_state.show_abstract = {}
        st.session_state.abstract_lang = {}
        st.session_state.translated_abstracts = {}
        
        try:
            # 翻译
            with st.status("🌐 正在处理问题...", expanded=True) as status:
                has_chinese = any('\u4e00' <= char <= '\u9fff' for char in query)
                
                if has_chinese:
                    st.write("检测到中文问题，正在翻译...")
                    translate_prompt = f"你是医学翻译专家。将用户的中文医学问题翻译成精确的英文医学术语，用于PubMed检索。只返回英文翻译，不要解释。\n\n翻译：{query}"
                    english_query = call_deepseek(translate_prompt, deepseek_api_key)
                    st.write(f"✅ 翻译结果: {english_query}")
                else:
                    english_query = query
                    st.write(f"✅ 搜索关键词: {english_query}")
                
                # 搜索PubMed
                st.write("正在检索PubMed数据库...")
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
                    status.update(label="❌ 未找到相关文献", state="error")
                    st.stop()
                
                st.write(f"✅ 找到 {len(pmids)} 篇相关文献")
                
                # 获取文献详情
                st.write("正在获取文献详情...")
                fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
                fetch_params = {
                    "db": "pubmed",
                    "id": ",".join(pmids),
                    "retmode": "xml"
                }
                fetch_response = requests.get(fetch_url, params=fetch_params, timeout=10)
                
                # 解析XML
                root = ET.fromstring(fetch_response.content)
                
                articles = []
                for article in root.findall(".//PubmedArticle"):
                    try:
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
                        
                        articles.append({
                            "title": str(title),
                            "abstract": str(abstract),
                            "journal": str(journal),
                            "year": str(year),
                            "pmid": str(pmid)
                        })
                    except Exception as e:
                        continue
                
                st.session_state.articles = articles
                st.session_state.query_done = True
                
                status.update(label="✅ 检索完成！", state="complete")
                        
        except Exception as e:
            st.error(f"❌ 发生错误: {str(e)}")

# 显示结果
if st.session_state.query_done and st.session_state.articles:
    st.markdown("---")
    st.markdown(f"### 📑 检索结果 ({len(st.session_state.articles)} 篇文献)")
    
    # 使用tabs展示多篇文献
    if len(st.session_state.articles) > 1:
        tabs = st.tabs([f"文献 {i+1}" for i in range(len(st.session_state.articles))])
    else:
        tabs = [st.container()]
    
    for idx, (tab, article) in enumerate(zip(tabs, st.session_state.articles), 1):
        with tab:
            # 文献标题
            st.subheader(article["title"])
            
            # 生成解读
            interpretation_key = f"interpretation_{article['pmid']}"
            
            if interpretation_key not in st.session_state:
                with st.spinner("🤖 AI正在生成临床解读..."):
                    prompt = f"""你是一名医学循证研究助手，需要帮助临床医生快速理解 PubMed 文献。

请基于提供的文献标题和摘要，生成一个"结构化临床解读"，要求医生在30秒内能够理解该研究的核心价值。

输出必须严格按照以下结构：

【一句话结论】
用一句话总结这篇研究最重要的结论，必须是临床决策相关的信息，而不是背景描述。

【证据标签】
研究类型：例如 RCT / Meta-analysis / Cohort study / Systematic review
证据等级：高 / 中 / 低（根据研究类型和样本量判断）
样本量：n=XXXX
期刊级别：顶级 / 高影响力 / 一般（例如 NEJM、Lancet、JAMA 可认为顶级）

【研究问题】
简要说明研究想回答的临床问题（1-2句话）

【关键结果】
列出2-4条最重要的研究发现，尽量包含具体数据或方向性结果。

【临床启示】
从临床医生角度总结研究意味着什么，例如：
- 是否支持某种治疗
- 是否建议改变临床策略
- 是否建议长期用药

【适用患者】
总结该研究结论最适合哪类患者，例如：
- 慢性肾病患者
- 2型糖尿病合并CKD
- 高心血管风险患者

【研究局限】
用2-3条简要说明研究局限，例如：
- 事后分析
- 样本量不足
- 未随机对照

输出要求：
1. 语言简洁、临床导向
2. 每个部分不超过3行
3. 避免重复摘要内容
4. 重点突出"临床意义"
5. 不要编造不存在的数据

文献信息如下：
标题：{article['title']}
摘要：{article['abstract']}
期刊：{article['journal']}
年份：{article['year']}
"""
                    
                    try:
                        interpretation = call_deepseek(prompt, deepseek_api_key)
                        st.session_state[interpretation_key] = interpretation
                    except Exception as e:
                        st.error(f"生成解读失败: {str(e)}")
                        st.session_state[interpretation_key] = None
            
            # 显示解读
            if st.session_state.get(interpretation_key):
                # 先提取一句话总结
                lines = st.session_state[interpretation_key].split('\n')
                conclusion_text = None
                current_section = None
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    if line.startswith('【') and line.endswith('】'):
                        section_name = line[1:-1]
                        if section_name == "一句话结论":
                            current_section = "conclusion"
                            continue
                    elif current_section == "conclusion":
                        conclusion_text = line
                        break
                
                # 开始卡片
                st.markdown('<div class="literature-card">', unsafe_allow_html=True)
                
                # 第一行：显示一句话总结
                if conclusion_text:
                    st.markdown(f'<div class="section-header">一句话总结</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="conclusion-highlight">{conclusion_text}</div>', unsafe_allow_html=True)
                
                # 然后渲染其他内容
                render_interpretation(st.session_state[interpretation_key])
                
                st.markdown('</div>', unsafe_allow_html=True)
                
                # 原文信息
                st.markdown('<div class="meta-info">', unsafe_allow_html=True)
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f"**期刊：** {article['journal']}")
                with col2:
                    st.markdown(f"**年份：** {article['year']}")
                with col3:
                    if article['pmid']:
                        st.markdown(f"[PMC 原文链接](https://pubmed.ncbi.nlm.nih.gov/{article['pmid']}/)")
                st.markdown('</div>', unsafe_allow_html=True)
                
                # 原文摘要
                abstract_key = f"show_abstract_{article['pmid']}"
                lang_key = f"lang_{article['pmid']}"
                
                if lang_key not in st.session_state.abstract_lang:
                    st.session_state.abstract_lang[lang_key] = "中"
                
                col_btn1, col_btn2 = st.columns([1, 5])
                with col_btn1:
                    if st.button(f"{'隐藏' if st.session_state.show_abstract.get(abstract_key, False) else '查看'}原文摘要", key=f"btn_{article['pmid']}"):
                        st.session_state.show_abstract[abstract_key] = not st.session_state.show_abstract.get(abstract_key, False)
                        st.rerun()
                
                with col_btn2:
                    if st.session_state.show_abstract.get(abstract_key, False):
                        current_lang = st.session_state.abstract_lang[lang_key]
                        if st.button(f"🌐 {current_lang}", key=f"lang_{article['pmid']}", help="点击切换中英文"):
                            st.session_state.abstract_lang[lang_key] = "EN" if current_lang == "中" else "中"
                            st.rerun()
                
                if st.session_state.show_abstract.get(abstract_key, False):
                    current_lang = st.session_state.abstract_lang[lang_key]
                    
                    if current_lang == "EN":
                        st.markdown(f'<div class="abstract-box">{article["abstract"]}</div>', unsafe_allow_html=True)
                    else:
                        translated_key = f"translated_{article['pmid']}"
                        if translated_key not in st.session_state.translated_abstracts:
                            with st.spinner("正在翻译..."):
                                try:
                                    translated = translate_abstract(article["abstract"], deepseek_api_key)
                                    st.session_state.translated_abstracts[translated_key] = translated
                                except Exception as e:
                                    st.session_state.translated_abstracts[translated_key] = f"翻译失败: {str(e)}"
                        
                        st.markdown(f'<div class="abstract-box">{st.session_state.translated_abstracts[translated_key]}</div>', unsafe_allow_html=True)
                
                # 关闭卡片
                st.markdown('</div>', unsafe_allow_html=True)

# 页脚
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #999; font-size: 0.8rem; padding: 20px 0;'>
    <p>⚠️ 本工具仅供临床参考，不构成医疗建议</p>
</div>
""", unsafe_allow_html=True)

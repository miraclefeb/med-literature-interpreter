import streamlit as st
import requests
import os
import xml.etree.ElementTree as ET
import re

# 页面配置
st.set_page_config(
    page_title="文献解读 PubMed 版",
    page_icon="📚",
    layout="wide"
)

# 自定义CSS样式
st.markdown("""
<style>
    /* 文献标题放大一个字号 */
    .stExpander summary p {
        font-size: 1.1rem !important;
        font-weight: 600 !important;
    }
    
    /* 结构化解读标题缩小一个字号 */
    h3 {
        font-size: 0.95rem !important;
    }
    
    /* 摘要区域样式 */
    .abstract-box {
        background-color: #f7f7f7;
        padding: 15px;
        border-radius: 8px;
        border-left: 3px solid #E8762D;
        margin-top: 10px;
    }
    
    /* 语言切换开关样式 */
    .lang-switch {
        display: inline-flex;
        align-items: center;
        background-color: #E5E7EB;
        border-radius: 20px;
        padding: 2px;
        font-size: 0.75rem;
        margin-left: 10px;
    }
    
    .lang-option {
        padding: 4px 12px;
        border-radius: 18px;
        cursor: pointer;
        transition: all 0.3s;
        color: #6B7280;
        font-weight: 500;
    }
    
    .lang-option.active {
        background-color: white;
        color: #1F2937;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    /* 研究类型标签样式 */
    .tag-rct {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 12px;
        background-color: #FFF4E6;
        color: #D97706;
        font-weight: 600;
        font-size: 0.85rem;
        margin: 2px;
    }
    
    .tag-meta {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 12px;
        background-color: #DBEAFE;
        color: #1E40AF;
        font-weight: 600;
        font-size: 0.85rem;
        margin: 2px;
    }
    
    .tag-cohort {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 12px;
        background-color: #D1FAE5;
        color: #047857;
        font-weight: 600;
        font-size: 0.85rem;
        margin: 2px;
    }
    
    .tag-review {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 12px;
        background-color: #E0E7FF;
        color: #4338CA;
        font-weight: 600;
        font-size: 0.85rem;
        margin: 2px;
    }
    
    .tag-case {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 12px;
        background-color: #FCE7F3;
        color: #BE185D;
        font-weight: 600;
        font-size: 0.85rem;
        margin: 2px;
    }
    
    .tag-other {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 12px;
        background-color: #F3F4F6;
        color: #4B5563;
        font-weight: 600;
        font-size: 0.85rem;
        margin: 2px;
    }
    
    /* 证据等级标签 */
    .tag-high {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 12px;
        background-color: #D1FAE5;
        color: #047857;
        font-weight: 600;
        font-size: 0.85rem;
        margin: 2px;
    }
    
    .tag-medium {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 12px;
        background-color: #FEF3C7;
        color: #B45309;
        font-weight: 600;
        font-size: 0.85rem;
        margin: 2px;
    }
    
    .tag-low {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 12px;
        background-color: #FEE2E2;
        color: #B91C1C;
        font-weight: 600;
        font-size: 0.85rem;
        margin: 2px;
    }
    
    /* 期刊级别标签 */
    .tag-top {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 12px;
        background-color: #FEF3C7;
        color: #B45309;
        font-weight: 600;
        font-size: 0.85rem;
        margin: 2px;
    }
    
    .tag-high-impact {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 12px;
        background-color: #E0E7FF;
        color: #4338CA;
        font-weight: 600;
        font-size: 0.85rem;
        margin: 2px;
    }
    
    .tag-general {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 12px;
        background-color: #F3F4F6;
        color: #6B7280;
        font-weight: 600;
        font-size: 0.85rem;
        margin: 2px;
    }
    
    /* 内容缩进样式 */
    .indent-content {
        margin-left: 20px;
        line-height: 1.8;
    }
    
    /* 章节标题样式 */
    .section-title {
        font-weight: 700;
        color: #1F2937;
        margin-top: 16px;
        margin-bottom: 8px;
    }
</style>
""", unsafe_allow_html=True)

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
    3. 生成结构化临床解读
    
    **解读维度：**
    - 一句话结论
    - 证据标签
    - 研究问题
    - 关键结果
    - 临床启示
    - 适用患者
    - 研究局限
    """)

def extract_text(element):
    """安全提取XML元素文本"""
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
    """调用DeepSeek API"""
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
    """翻译摘要为中文"""
    try:
        prompt = f"请将以下英文医学摘要翻译成中文，保持专业术语准确：\n\n{abstract}"
        return call_deepseek(prompt, api_key)
    except Exception as e:
        return f"翻译失败: {str(e)}"

def format_interpretation(text: str) -> str:
    """格式化解读文本，添加标签和缩进"""
    lines = text.split('\n')
    formatted_lines = []
    current_section = None
    
    for line in lines:
        line = line.strip()
        if not line:
            formatted_lines.append("")
            continue
        
        # 检测章节标题
        if line.startswith('【') and line.endswith('】'):
            formatted_lines.append(f'<div class="section-title">{line}</div>')
            current_section = line
        # 处理证据标签部分
        elif current_section == '【证据标签】':
            # 研究类型标签
            if '研究类型：' in line or '研究类型:' in line:
                content = line.split('：')[-1].split(':')[-1].strip()
                tag_class = 'tag-other'
                if 'RCT' in content.upper():
                    tag_class = 'tag-rct'
                elif 'Meta' in content or 'meta' in content:
                    tag_class = 'tag-meta'
                elif 'Cohort' in content or 'cohort' in content or '队列' in content:
                    tag_class = 'tag-cohort'
                elif 'Review' in content or 'review' in content or '综述' in content:
                    tag_class = 'tag-review'
                elif 'Case' in content or 'case' in content or '病例' in content:
                    tag_class = 'tag-case'
                formatted_lines.append(f'<div class="indent-content">研究类型：<span class="{tag_class}">{content}</span></div>')
            # 证据等级标签
            elif '证据等级：' in line or '证据等级:' in line:
                content = line.split('：')[-1].split(':')[-1].strip()
                tag_class = 'tag-medium'
                if '高' in content:
                    tag_class = 'tag-high'
                elif '低' in content:
                    tag_class = 'tag-low'
                formatted_lines.append(f'<div class="indent-content">证据等级：<span class="{tag_class}">{content}</span></div>')
            # 期刊级别标签
            elif '期刊级别：' in line or '期刊级别:' in line:
                content = line.split('：')[-1].split(':')[-1].strip()
                tag_class = 'tag-general'
                if '顶级' in content:
                    tag_class = 'tag-top'
                elif '高影响力' in content:
                    tag_class = 'tag-high-impact'
                formatted_lines.append(f'<div class="indent-content">期刊级别：<span class="{tag_class}">{content}</span></div>')
            # 其他内容
            else:
                formatted_lines.append(f'<div class="indent-content">{line}</div>')
        # 其他章节内容缩进
        elif current_section:
            formatted_lines.append(f'<div class="indent-content">{line}</div>')
        else:
            formatted_lines.append(line)
    
    return '\n'.join(formatted_lines)

# 使用session_state保存结果，防止刷新丢失
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

# 主界面
query = st.text_input(
    "🔍 输入医学问题（中文/英文均可）",
    placeholder="例如：SGLT2抑制剂在心血管疾病中的作用",
    key="query_input"
)

if st.button("🚀 开始解读", type="primary"):
    if not query:
        st.warning("请输入问题")
    elif not deepseek_api_key:
        st.error("请在侧边栏配置 DeepSeek API Key")
    else:
        # 清空之前的结果
        st.session_state.articles = []
        st.session_state.query_done = False
        st.session_state.show_abstract = {}
        st.session_state.abstract_lang = {}
        st.session_state.translated_abstracts = {}
        
        try:
            # 1. 翻译问题为英文（如果是中文）
            with st.spinner("正在处理问题..."):
                has_chinese = any('\u4e00' <= char <= '\u9fff' for char in query)
                
                if has_chinese:
                    st.info("🌐 检测到中文问题，正在翻译为英文...")
                    translate_prompt = f"你是医学翻译专家。将用户的中文医学问题翻译成精确的英文医学术语，用于PubMed检索。只返回英文翻译，不要解释。\n\n翻译：{query}"
                    english_query = call_deepseek(translate_prompt, deepseek_api_key)
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
                    st.warning("未找到相关文献")
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
                    
                    # 保存到session_state
                    st.session_state.articles = articles
                    st.session_state.query_done = True
                        
        except Exception as e:
            st.error(f"发生错误: {str(e)}")

# 显示结果（从session_state读取，不会因为刷新丢失）
if st.session_state.query_done and st.session_state.articles:
    for idx, article in enumerate(st.session_state.articles, 1):
        with st.expander(f"📄 文献 {idx}: {article['title'][:80]}...", expanded=(idx==1)):
            # 检查是否已经生成过解读
            interpretation_key = f"interpretation_{article['pmid']}"
            
            if interpretation_key not in st.session_state:
                # 第一次生成解读
                with st.spinner("正在生成解读..."):
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
            
            # 显示解读（从session_state读取）
            if st.session_state.get(interpretation_key):
                st.markdown("### 📎 结构化临床解读")
                # 格式化并显示
                formatted_text = format_interpretation(st.session_state[interpretation_key])
                st.markdown(formatted_text, unsafe_allow_html=True)
                
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
                        st.markdown(f"[PMC](https://pubmed.ncbi.nlm.nih.gov/{article['pmid']}/)")
                
                # 显示/隐藏摘要按钮
                abstract_key = f"show_abstract_{article['pmid']}"
                lang_key = f"lang_{article['pmid']}"
                
                # 初始化语言状态（默认英文）
                if lang_key not in st.session_state.abstract_lang:
                    st.session_state.abstract_lang[lang_key] = "en"
                
                col_btn1, col_btn2 = st.columns([1, 5])
                with col_btn1:
                    if st.button(f"{'隐藏' if st.session_state.show_abstract.get(abstract_key, False) else '查看'}原文摘要", key=f"btn_{article['pmid']}"):
                        st.session_state.show_abstract[abstract_key] = not st.session_state.show_abstract.get(abstract_key, False)
                        st.rerun()
                
                with col_btn2:
                    if st.session_state.show_abstract.get(abstract_key, False):
                        # 语言切换滑块
                        current_lang = st.session_state.abstract_lang[lang_key]
                        
                        col_en, col_zh = st.columns(2)
                        with col_en:
                            if st.button("英", key=f"en_{article['pmid']}", disabled=(current_lang=="en")):
                                st.session_state.abstract_lang[lang_key] = "en"
                                st.rerun()
                        with col_zh:
                            if st.button("中", key=f"zh_{article['pmid']}", disabled=(current_lang=="zh")):
                                st.session_state.abstract_lang[lang_key] = "zh"
                                st.rerun()
                
                # 显示摘要（如果按钮被点击）
                if st.session_state.show_abstract.get(abstract_key, False):
                    current_lang = st.session_state.abstract_lang[lang_key]
                    
                    if current_lang == "en":
                        # 显示英文原文
                        st.markdown(f'<div class="abstract-box">{article["abstract"]}</div>', unsafe_allow_html=True)
                    else:
                        # 显示中文翻译
                        translated_key = f"translated_{article['pmid']}"
                        if translated_key not in st.session_state.translated_abstracts:
                            with st.spinner("正在翻译..."):
                                try:
                                    translated = translate_abstract(article["abstract"], deepseek_api_key)
                                    st.session_state.translated_abstracts[translated_key] = translated
                                except Exception as e:
                                    st.session_state.translated_abstracts[translated_key] = f"翻译失败: {str(e)}"
                        
                        st.markdown(f'<div class="abstract-box">{st.session_state.translated_abstracts[translated_key]}</div>', unsafe_allow_html=True)

# 页脚
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9em;'>
    <p>数据来源：PubMed | AI解读：DeepSeek</p>
    <p>⚠️ 仅供参考，不构成医疗建议</p>
</div>
""", unsafe_allow_html=True)

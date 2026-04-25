"""检索模块 - 混合检索 + 重排序"""
from typing import Optional

from langchain_chroma import Chroma


def hybrid_search(
    chroma: Chroma,
    query: str,
    query_keywords: list[str],
    top_k: int = 5,
    filters: dict | None = None,
    keyword_weight: float = 0.3,
    vector_weight: float = 0.7,
) -> list[dict]:
    """
    混合检索：向量相似度 + 关键词 where_document 过滤 + 重排序

    1. 向量相似度检索（扩大召回，取 top_k * 2）
    2. 关键词过滤（where_document $contains）
    3. 重排序：基于关键词重叠度调整分数
    """
    try:
        # 向量检索，扩大召回范围
        expanded_k = top_k * 2
        if filters:
            vector_results = chroma.similarity_search(query, k=expanded_k, filter=filters)
        else:
            vector_results = chroma.similarity_search(query, k=expanded_k)

        if not vector_results:
            return []

        # 重排序：基于关键词重叠度
        scored_results = []
        for doc in vector_results:
            content = doc.page_content.lower()
            # 计算关键词重叠度
            overlap_count = sum(1 for kw in query_keywords if kw.lower() in content)
            keyword_score = overlap_count / max(len(query_keywords), 1)

            # 综合得分（向量检索的排序隐含了向量相似度，越靠前分数越高）
            # 这里用位置作为向量分数的代理
            idx = vector_results.index(doc)
            vector_score = 1.0 - (idx / max(len(vector_results), 1))

            final_score = vector_weight * vector_score + keyword_weight * keyword_score
            scored_results.append({
                "content": doc.page_content,
                "metadata": doc.metadata,
                "score": final_score,
            })

        # 按综合得分排序，取 top_k
        scored_results.sort(key=lambda x: x["score"], reverse=True)
        return scored_results[:top_k]
    except Exception:
        return []


def extract_keywords(query: str) -> list[str]:
    """
    从查询中提取关键词（简单分词：按空格和标点分割，过滤停用词）
    """
    import re
    # 移除标点，按空格分割
    words = re.split(r'[\s,，。！？、；：""''（）\(\)\[\]【】]+', query)
    stop_words = {'的', '了', '是', '在', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这', '他', '她', '它', '我', '什么', '那', '被', '从', '把', '让', '用', '为', '与', '对', '而', '但', '又', '吗', '呢', '吧', '啊', '哦', '嗯', '呀', '哪', '谁', '怎么', '如何', '为什么', '可以', '能', '这个', '那个', '什么', '怎么'}
    keywords = [w.strip() for w in words if w.strip() and w.strip() not in stop_words and len(w.strip()) > 0]
    return keywords

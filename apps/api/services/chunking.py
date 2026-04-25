"""文本分块模块 - 支持双层分块策略"""
from langchain_text_splitters import RecursiveCharacterTextSplitter


def create_paragraph_splitter(
    chunk_size: int = 500,
    chunk_overlap: int = 50,
) -> RecursiveCharacterTextSplitter:
    """创建段落级分块器（细粒度，用于精确检索）"""
    return RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", "。", "！", "？", "；", ""],
    )


def create_plot_splitter(
    chunk_size: int = 1000,
    chunk_overlap: int = 100,
) -> RecursiveCharacterTextSplitter:
    """创建关键剧情点级分块器（粗粒度，用于上下文理解）"""
    return RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", "。", ""],
    )


def dual_layer_chunk(content: str) -> tuple[list[str], list[str]]:
    """
    双层分块：返回 (paragraph_chunks, plot_chunks)
    """
    paragraph_splitter = create_paragraph_splitter()
    plot_splitter = create_plot_splitter()
    return paragraph_splitter.split_text(content), plot_splitter.split_text(content)

'''
Date         : 2026-08-16 14:57:49
LastEditTime : 2026-08-16 15:29:12
'''
import os
import hashlib
from pypdf import PdfReader
import chromadb
from chromadb.utils import embedding_functions

_chroma_client = None
_collection = None

# 使用 Chroma 内置的 ONNX 嵌入
def get_embedding_function():
    return embedding_functions.ONNXMiniLM_L6_V2()

def get_collection():
    global _chroma_client, _collection
    
    if _collection is not None:
        return _collection
    
    _chroma_client = chromadb.PersistentClient(path="./chroma_db")
    _collection = _chroma_client.get_or_create_collection(
        name="papers",
        embedding_function=get_embedding_function()
    )
    return _collection


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 100) -> list:
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        if chunk.strip():
            chunks.append(chunk)
    return chunks


def index_paper(filepath: str) -> str:
    """
    将论文PDF分块并存入向量数据库
    支持 paper_id 或 filepath 参数
    """
    # 兼容两种参数名
    if filepath is None and paper_id is not None:
        filepath = paper_id
    
    if filepath is None:
        return "❌ 请提供文件名"
    
    try:
        if not os.path.exists(filepath):
            test_path = os.path.join("papers", filepath)
            if os.path.exists(test_path):
                filepath = test_path
            else:
                return f"❌ 文件不存在：{filepath}"
        
        reader = PdfReader(filepath)
        full_text = ""
        for page in reader.pages:
            full_text += page.extract_text() + "\n\n"
        
        doc_id = hashlib.md5(filepath.encode()).hexdigest()
        chunks = chunk_text(full_text, chunk_size=500, overlap=100)
        
        if not chunks:
            return "❌ 无法从PDF中提取文本内容"
        
        collection = get_collection()
        
        ids = [f"{doc_id}_{i}" for i in range(len(chunks))]
        documents = chunks
        metadatas = [{"source": filepath, "chunk_index": i} for i in range(len(chunks))]
        
        existing = collection.get(ids=ids)
        if existing['ids']:
            collection.delete(ids=existing['ids'])
        
        collection.add(ids=ids, documents=documents, metadatas=metadatas)
        
        return f"✅ 论文已索引：{os.path.basename(filepath)}，共 {len(chunks)} 个块"
        
    except Exception as e:
        return f"❌ 索引失败：{str(e)}"


def ask_paper(question: str, openai_client, filepath: str = None, top_k: int = 5) -> str:
    try:
        print("[DEBUG 1] 进入 ask_paper")
        collection = get_collection()
        print(f"[DEBUG 2] 集合文档数: {collection.count()}")
        
        if collection.count() == 0:
            return "❌ 向量数据库为空"
        
        where_filter = None
        if filepath:
            # ✅ 修复：补全路径，匹配数据库中存储的格式
            if not filepath.startswith("papers"):
                filepath = os.path.join("papers", filepath)
            where_filter = {"source": filepath}
            print(f"[DEBUG 3] 查询过滤条件: {where_filter}")
        
        print("[DEBUG 4] 开始 Chroma 查询...")
        results = collection.query(
            query_texts=[question],
            n_results=top_k,
            where=where_filter
        )
        print(f"[DEBUG 5] Chroma 查询完成，找到 {len(results['documents'][0]) if results['documents'] else 0} 个结果")
        
        if not results['documents'] or not results['documents'][0]:
            return "❌ 未找到相关内容"
        
        print(f"[DEBUG 6] 找到 {len(results['documents'][0])} 个结果")
        context = "\n\n---\n\n".join(results['documents'][0])
        print(f"[DEBUG 7] 上下文长度: {len(context)} 字符")
        
        print("[DEBUG 8] 开始调用大模型...")
        response = openai_client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": f"基于以下内容回答问题：\n\n{context}\n\n问题：{question}"}],
            temperature=0.3,
            max_tokens=1000,
            timeout=30
        )
        print("[DEBUG 9] 大模型调用完成")
        
        answer = response.choices[0].message.content
        return f"📚 **基于论文内容的回答：**\n\n{answer}"
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return f"❌ 检索失败：{str(e)}"


def get_paper_status() -> str:
    try:
        collection = get_collection()
        count = collection.count()
        
        if count == 0:
            return "📊 向量数据库为空，还没有索引任何论文"
        
        all_data = collection.get()
        sources = set()
        for meta in all_data['metadatas']:
            if meta and 'source' in meta:
                sources.add(meta['source'])
        
        return f"📊 向量数据库状态：\n- 总块数：{count}\n- 已索引论文：{len(sources)} 篇\n- 论文列表：{', '.join([os.path.basename(s) for s in sources])}"
        
    except Exception as e:
        return f"❌ 获取状态失败：{str(e)}"
import faiss
import numpy as np
import pickle
from utils.log_utils import logger
from config import Config
import os

class VectorIndexer:

    def __init__(self):
        self.index = None
        self.metadata = []
        self.index_file = os.path.join(Config.INDEX_PATH, Config.INDEX_FILE)
        self.metadata_file = os.path.join(Config.INDEX_PATH, Config.METADATA_FILE)

    def build_index(self, embeddings: list, metadata: list):
        """构建FAISS向量索引，并保存到磁盘"""
        dim = len(embeddings[0])
        self.index = faiss.IndexFlatL2(dim)
        self.index.add(np.array(embeddings))
        self.metadata = metadata
        
        # 保存索引和元数据到文件
        faiss.write_index(self.index, self.index_file)
        with open(self.metadata_file, "wb") as f:
            pickle.dump(self.metadata, f)
        logger.info(f"Saved index to {self.index_file} and metadata to {self.metadata_file}")
    
    def load_index(self):
        """加载已存储的向量索引和元数据"""
        if os.path.exists(self.index_file) and os.path.exists(self.metadata_file):
            self.index = faiss.read_index(self.index_file)
            with open(self.metadata_file, "rb") as f:
                self.metadata = pickle.load(f)
            logger.info(f"Loaded index from {self.index_file} and metadata from {self.metadata_file}")
            return True
        else:
            logger.warning(f"Index file or metadata file does not exist at {self.index_file} or {self.metadata_file}")
            return False
    
    def search(self, query_embedding: np.ndarray, top_k: int = 5):
        """搜索相似向量"""
        distances, indices = self.index.search(np.array([query_embedding]), top_k)
        # logger.info(f"distances: {distances, indices}")
        return [
            {
                "metadata": self.metadata[i], 
                "distance": distances[0][idx]
            }
            for idx, i in enumerate(indices[0])
            if i < len(self.metadata)
        ]
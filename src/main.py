import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import argparse
import pickle
from code_parser import CodeParser
from preprocessor import CodePreprocessor
from embedder import CodeEmbedder
from indexer import VectorIndexer
from similarity import SimilarityCalculator
from config import Config
import warnings
from utils.log_utils import *



warnings.filterwarnings("ignore", category=FutureWarning)
os.environ["KMP_DUPLICATE_LIB_OK"] = "True"

def main():
    parser = argparse.ArgumentParser(description="Code Similarity Detector")
    parser.add_argument("--repo", required=False, help="Target repository URL", default="https://github.com/satomic/copilot-usage-advanced-dashboard.git")
    parser.add_argument("--snippet", required=False, help="Query code snippet file", default="tmp/example.py")
    args = parser.parse_args()

    parser = CodeParser()

    os.makedirs(Config.INDEX_PATH, exist_ok=True)
    embeddings_file_path = os.path.join(
        Config.INDEX_PATH,
        Config.EMBEDDINGS_FILE
    )
    preprocessor = CodePreprocessor()
    embedder = CodeEmbedder()


    loaded = True # True False
    if os.path.exists(embeddings_file_path):
        with open(embeddings_file_path, "rb") as f:
            embeddings, processed_blocks = pickle.load(f)
            logger.info(f"Loaded {len(embeddings)} embeddings from file")

    if not loaded:
        # 1. 克隆仓库并解析代码
        code_blocks = parser.parse_repository(args.repo)
        logger.info(f"Found {len(code_blocks)} code blocks in the repository")

        # 2. 预处理代码
        processed_blocks = [preprocessor.process(b) for b in code_blocks]
        logger.info("Preprocessing completed")
        
        # 3. 生成嵌入向量
        embeddings = embedder.generate_embeddings(processed_blocks)
        with open(embeddings_file_path, "wb") as f:
            pickle.dump((embeddings, processed_blocks), f)
            logger.info(f"Saved {len(embeddings)} embeddings to file")


    # 4. 构建索引
    indexer = VectorIndexer()
    if not indexer.load_index():
        indexer.build_index(embeddings, processed_blocks)  # Pass metadata here

    # 5. 查询相似代码
    with open(args.snippet, "r", encoding="utf-8") as f:
        query_code = f.read()

    query_processed = preprocessor.process({"code": query_code, "file": args.snippet})
    query_embedding = embedder.generate_embeddings([query_processed])[0]

    # 6. 计算相似度
    similar_items = indexer.search(query_embedding, top_k=Config.TOP_K_RESULTS)
    calculator = SimilarityCalculator()
    results = calculator.calculate_similarity(query_processed, similar_items)

    # 7. 输出结果
    for res in results:
        print(f"Similarity: {res['similarity']:.2f}")
        # print(f"Text: {res['similarity_text']:.2f}")
        # print(f"Vect: {res['similarity_vector']:.2f}")
        print(f"File: {res['file']}")
        # print(f"Original Code:\n{res['code']}\n")

if __name__ == "__main__":
    main()
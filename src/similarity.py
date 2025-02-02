import difflib
from src.config import Config

class SimilarityCalculator:

    def calculate_similarity(self, query_block: dict, candidates: list):

        """综合计算相似度"""
        results = []
        for cand in candidates:
            metadata = cand["metadata"]
            distance = cand["distance"]

            similarity_text = difflib.SequenceMatcher(
                None, 
                query_block["normalized_code"], 
                metadata["normalized_code"]
            ).ratio()
            
            # 向量相似度
            similarity_vector = 1 / (1 + distance)
            
            # 综合得分
            combined_score = (1 - Config.text_vector_ratio) * similarity_vector + Config.text_vector_ratio * similarity_text  # 调整权重
            results.append({
                **metadata,
                "similarity": combined_score,
                "similarity_text": similarity_text,
                "similarity_vector": similarity_vector
            })
        
        return sorted(results, key=lambda x: x["similarity"], reverse=True)
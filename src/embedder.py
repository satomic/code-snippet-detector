from transformers import AutoTokenizer, AutoModel
import torch
from utils.log_utils import *
from config import Config

class CodeEmbedder:
    
    def __init__(self):
        """Initialize the CodeBERT embedder.

        The model and tokenizer are loaded from either local cache or downloaded from Hugging Face.
        Downloaded models are cached in:
        - Windows: C:/Users/<username>/.cache/huggingface/
        - Linux: ~/.cache/huggingface/
        - macOS: ~/Library/Caches/huggingface/

        Args:
            None

        Returns:
            None

        Raises:
            None, but logs info message if model needs to be downloaded
        """
        model_name = Config.MODEL_NAME
        try:
            # Try loading from local cache first
            self.tokenizer = AutoTokenizer.from_pretrained(model_name, local_files_only=True)
            self.model = AutoModel.from_pretrained(model_name, local_files_only=True)
            logger.info(f"Loaded local model {model_name}")
        except Exception:
            # If local files not found, download from internet
            logger.info(f"Local model not found, downloading {model_name}...")
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModel.from_pretrained(model_name)
            logger.info(f"Downloaded model {model_name}")

    def generate_embeddings(self, code_blocks: list, max_length=512) -> list:
        """生成代码块的向量表示"""
        # print("Generating embeddings...", code_blocks)
        embeddings = []
        for block in code_blocks:
            inputs = self.tokenizer(
                block["normalized_code"], 
                return_tensors="pt", 
                truncation=True,
                max_length=max_length,
                # cleanup_tokenization_spaces=False,
                # clean_up_tokenization_spaces=False,
            )
            with torch.no_grad():
                outputs = self.model(**inputs)
            embeddings.append(outputs.last_hidden_state.mean(dim=1).cpu().numpy()[0])
        return embeddings
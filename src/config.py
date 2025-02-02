class Config:
    REPO_STORAGE_PATH = "data/repos"
    INDEX_PATH = "data/indices"
    # MODEL_NAME = "microsoft/codebert-base" # https://huggingface.co/microsoft/codebert-base
    MODEL_NAME = "microsoft/unixcoder-base" # https://huggingface.co/microsoft/unixcoder-base
    TOP_K_RESULTS = 5
    EMBEDDINGS_FILE = "embeddings.pkl"
    INDEX_FILE = "index.faiss"
    METADATA_FILE = "metadata.pkl"
    text_vector_ratio = 1.0
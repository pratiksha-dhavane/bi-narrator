from llama_cpp import Llama
from functools import lru_cache
import threading

_MODEL_PATH = "model\mistral-7b-instruct-v0.2.Q4_K_M.gguf"
_LOCK = threading.Lock()

@lru_cache(maxsize=1)
def _get_llm(n_threads: int=6, n_ctx: int=4096):
    # cached singleton llm instance
    with _LOCK:
        return Llama(model_path=_MODEL_PATH, n_threads=n_threads, n_ctx=n_ctx)
    
def call_llm_local(prompt: str,
                   max_tokens: int = 500,
                   temperature: float = 0.1,
                   n_threads: int = 6,
                   n_ctx: int = 4096) -> str:
    """
    Single wrapper returning generated text
    """

    llm = _get_llm(n_threads=n_threads, n_ctx=n_ctx)
    out = llm(prompt=prompt, max_tokens=max_tokens, temperature=temperature)
    text =  out.get("choices", [{}])[0].get("text", "") or out.get("text", "")
    return text.strip()
import numpy as np
import pandas as pd
from typing import Optional, Dict, Any

from config import MAX_OUTPUT_TOKENS, TEMPERATURE

from analytics_layer import run_analytics
from format_prompt_layer import format_prompt_from_template
from llm import call_llm_local

from langchain_core.runnables import RunnableLambda, RunnableParallel
from functools import partial


analytics_runnable = RunnableLambda(lambda ctx: run_analytics(
    data=ctx["data"],
    date_col=ctx["date_col"],
    metric_col=ctx["metric_col"],
    category_col=ctx.get("category_col"), 
))

format_prompt = RunnableLambda(format_prompt_from_template)

call_llm = RunnableLambda(partial(call_llm_local, max_tokens=MAX_OUTPUT_TOKENS, temperature=TEMPERATURE))

chain = ( RunnableParallel({ "analytics_result" : analytics_runnable, 
                             "prompt_input" : (lambda x : x["prompt_input"])
                            }) 
          | format_prompt
          | call_llm
         )
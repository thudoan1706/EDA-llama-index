"""Relevancy evaluation."""

from __future__ import annotations

import asyncio
from typing import Any, Optional, Sequence, Union

from llama_index.core.evaluation.base import BaseEvaluator, EvaluationResult
from llama_index.core.indices import SummaryIndex
from llama_index.core.llms.llm import LLM
from llama_index.core.prompts import BasePromptTemplate, PromptTemplate
from llama_index.core.prompts.mixin import PromptDictType
from llama_index.core.schema import Document
from llama_index.core.settings import Settings
from llama_index.core.evaluation import RelevancyEvaluator


class CustomRelevancyEvaluator(RelevancyEvaluator):
    """Relenvancy evaluator."""


    async def aevaluate(
        self,
        query: str | None = None,
        response: str | None = None,
        contexts: Sequence[str] | None = None,
        sleep_time_in_seconds: int = 0,
        **kwargs: Any,
    ) -> EvaluationResult:
        """Evaluate whether the contexts and response are relevant to the query."""
        del kwargs  # Unused

        if query is None or contexts is None:
            raise ValueError("query, contexts, and response must be provided")

        docs = [Document(text=context) for context in contexts]
        index = SummaryIndex.from_documents(docs)

        query_response = f"Question: {query}"

        await asyncio.sleep(sleep_time_in_seconds)

        query_engine = index.as_query_engine(
            llm=self._llm,
            text_qa_template=self._eval_template,
            refine_template=self._refine_template,
        )
        response_obj = await query_engine.aquery(query_response)

        raw_response_txt = str(response_obj)

        if "yes" in raw_response_txt.lower():
            passing = True
        else:
            if self._raise_error:
                raise ValueError("The response is invalid")
            passing = False

        return EvaluationResult(
            query=query,
            response=response,
            passing=passing,
            score=1.0 if passing else 0.0,
            feedback=raw_response_txt,
            contexts=contexts,
        )

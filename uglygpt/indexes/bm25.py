#!/usr/bin/env python3
# -*-coding:utf-8-*-

import asyncio
import concurrent.futures
import heapq
import itertools
import json
import string
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Set, Tuple, Dict

import jieba
from loguru import logger
from nltk.text import TextCollection

from .base import DB
from uglygpt.base import config


stop_words = set(
    line.strip() for line in
    Path(config.stop_words_path).read_text(encoding='utf-8').splitlines()
)


class PathNotFoundError(Exception):
    pass


@dataclass
class BM25:
    k1: float = 1.5
    b: float = 0.75
    texts: List[str] = field(default_factory=list)
    metadatas: List[Dict[str, str]] = field(default_factory=list)
    text_collection: TextCollection = field(init=False)
    preprocessed_texts: List[str] = field(default_factory=list)
    word_sets: List[Set[str]] = field(default_factory=list)
    text_lens: List[int] = field(default_factory=list)
    tf_idf_values: dict = field(default_factory=dict)
    tf_values: dict = field(default_factory=dict)
    sum_len: float = field(default=0)

    def preprocess_text(self, text: str) -> str:
        words = jieba.cut(text)
        words = [
            word for word in words
            if word not in stop_words and word not in string.punctuation
        ]
        return ' '.join(words)

    def calculate_bm25_score(self, i: int, query: str) -> float:
        score = 0
        preprocessed_query = self.preprocess_text(query).split()
        for word in preprocessed_query:
            if word not in self.word_sets[i]:
                continue
            key = f"{word}_{i}"
            tf_idf_value = self.tf_idf_values.get(key, 0)
            tf_value = self.tf_values.get(key, 1e-9)
            text_len = self.text_lens[i]
            avg_len = self.sum_len / \
                len(self.preprocessed_texts) if self.preprocessed_texts else 1
            score_part = (
                (self.k1 + 1) /
                (tf_value + self.k1 * (1 - self.b + self.b * text_len / avg_len))
            )
            score += tf_idf_value * score_part
        return score

    def search(self, query: str, n: int = DB.default_n) -> List[Tuple[str, float]]:
        if not query or self.is_empty:
            return []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            scores = list(executor.map(self.calculate_bm25_score,
                            range(len(self.texts)), itertools.repeat(query)))
        scores = list(zip(self.texts, scores))
        top_n_scores = heapq.nlargest(n, scores, key=lambda x: x[1])
        return top_n_scores

    def add(self, text: str, metadata: Dict[str, str] = {}) -> None:
        if text in self.texts:
            logger.warning(f"Text already exists: {text}")
            return
        text_id = len(self.texts)
        self.texts.append(text)
        self.metadatas.append(metadata)
        preprocessed_text = self.preprocess_text(text)
        preprocessed_text_split = preprocessed_text.split()
        self.preprocessed_texts.append(preprocessed_text)
        self.text_collection = TextCollection(self.preprocessed_texts)
        self.sum_len += len(preprocessed_text_split)
        self.word_sets.append(set(preprocessed_text_split))
        self.text_lens.append(len(preprocessed_text_split))
        for word in self.word_sets[text_id]:
            key = f"{word}_{text_id}"
            self.tf_idf_values[key] = self.text_collection.tf_idf(word, text)
            self.tf_values[key] = self.text_collection.tf(word, text)

    @property
    def is_empty(self):
        return not self.texts


@dataclass
class BM25DB(DB):
    _data: BM25 = field(init=False)

    def __post_init__(self):
        super().__post_init__()

    def search(self, query: str, n: int = DB.default_n) -> List[str]:
        top_n_scores = self._data.search(query, n)
        return [text for text, _ in top_n_scores]

    def add(self, text: str, metadata: Dict[str, str] = {}) -> None:
        if not text:
            logger.warning("Text cannot be empty.")
            return
        self._data.add(text, metadata)
        asyncio.run(self._save())

    def init(self) -> None:
        if not hasattr(self, '_data') or not self._data or not self._data.is_empty:
            self._data = BM25()

    async def _save(self) -> None:
        if not self.path:
            raise PathNotFoundError("Path not found, unable to save.")
        data = self._data.__dict__.copy()
        text_collection = data.pop('text_collection')
        data['word_sets'] = [list(v) for v in data['word_sets']]
        with open(self.path, 'w') as f:
            json.dump(data, f)
        self._data.text_collection = text_collection
        self._data.word_sets = [set(v) for v in data['word_sets']]

    def _load(self) -> None:
        if self.path and Path(self.path).exists():
            try:
                with open(self.path, 'r') as f:
                    data = json.load(f)
                data['word_sets'] = [set(v) for v in data['word_sets']]
                self._data = BM25(**data)
                self._data.text_collection = TextCollection(self._data.preprocessed_texts)
                return
            except json.JSONDecodeError as e:
                logger.error(e)
                raise
        self.init()
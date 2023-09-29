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
from typing import List, Set

import jieba
from loguru import logger
from nltk.text import TextCollection

from .base import DB
from uglygpt.base import config


stop_words = set(
    line.strip() for line in
    Path(config.stop_words_path).read_text(encoding='utf-8').splitlines()
)


@dataclass
class BM25:
    file_path: str
    texts: List[str] = field(default_factory=list)
    k1: float = 1.5
    b: float = 0.75
    text_collection: TextCollection = field(init=False)
    preprocessed_texts: List[str] = field(default_factory=list)
    word_sets: List[Set[str]] = field(default_factory=list)
    text_lens: List[int] = field(default_factory=list)
    tf_idf_values: dict = field(default_factory=dict)
    tf_values: dict = field(default_factory=dict)
    sum_len: float = field(default=0)

    def __post_init__(self):
        for text in list(self.texts):
            self.add(text)

    def preprocess_text(self, text: str) -> str:
        words = jieba.cut(text)
        words = [
            word for word in words
            if word not in stop_words and word not in string.punctuation
        ]
        return ' '.join(words)

    def calculate_bm25_score(self, i: int, query: str) -> float:
        score = 0
        preprocessed_query = self.preprocess_text(query)
        for word in preprocessed_query.split():
            if word not in self.word_sets[i]:
                continue
            key = f"{word}_{i}"
            tf_idf_value = self.tf_idf_values.get(key, 0)
            tf_value = self.tf_values.get(key, 1e-9)
            text_len = self.text_lens[i]
            avg_len = self.sum_len / len(self.preprocessed_texts) if self.preprocessed_texts else 1
            score_part = (
                (self.k1 + 1) /
                (tf_value + self.k1 * (1 - self.b + self.b * text_len / avg_len))
            )
            score += tf_idf_value * score_part
        return score

    def search(self, query: str, n: int = DB.default_n) -> List[str]:
        if not query or self.is_empty():
            return []

        with concurrent.futures.ThreadPoolExecutor() as executor:
            scores = list(executor.map(self.calculate_bm25_score, range(len(self.texts)), itertools.repeat(query)))
        scores = list(zip(self.texts, scores))
        top_n_scores = heapq.nlargest(n, scores, key=lambda x: x[1])
        return [text for text, _ in top_n_scores]

    def add(self, text: str):
        if not text:
            return "Text cannot be empty."
        if text in self.texts:
            return "Text already exists."
        id = len(self.texts)
        self.texts.append(text)
        preprocessed_text = self.preprocess_text(text)
        self.preprocessed_texts.append(preprocessed_text)
        self.text_collection = TextCollection(self.preprocessed_texts)
        self.sum_len += len(preprocessed_text.split())
        self.word_sets.append(set(preprocessed_text.split()))
        self.text_lens.append(len(preprocessed_text.split()))
        for word in self.word_sets[id]:
            key = f"{word}_{id}"
            self.tf_idf_values[key] = self.text_collection.tf_idf(word, text)
            self.tf_values[key] = self.text_collection.tf(word, text)
        if self.file_path:
            asyncio.run(self._save())

    async def _save(self):
        text_collection = self.text_collection
        del self.text_collection
        self.word_sets = [list(v) for v in self.word_sets] # type: ignore
        with open(self.file_path, 'w') as f:
            json.dump(self.__dict__, f)
        self.text_collection = text_collection
        self.word_sets = [set(v) for v in self.word_sets]

    @classmethod
    def load(cls, file_path: str):
        with open(file_path, 'r') as f:
            data = json.load(f)
        del data['file_path']
        data['word_sets'] = [set(v) for v in data['word_sets']]
        instance = cls(file_path, **data)
        instance.text_collection = TextCollection(instance.preprocessed_texts)
        return instance

    def is_empty(self):
        return len(self.texts) == 0


@dataclass
class BM25DB(DB):
    file_path: str
    _data: BM25 = field(init=False)

    def __post_init__(self):
        if self.file_path and Path(self.file_path).exists():
            try:
                self._data = BM25.load(self.file_path)
            except Exception as e:  # TODO: 无法导入也有可能可被修复，所以这里还需要更多的判断。
                logger.error(e)
                logger.warning(f"无法导入 {self.file_path}，将重新初始化")
                self.init()
        else:
            Path(self.file_path).touch()
            self.init()

    def search(self, query: str, n: int = DB.default_n) -> List[str]:
        return self._data.search(query, n)

    def add(self, text: str):
        self._data.add(text)

    def init(self):
        if hasattr(self, '_data') and self._data and self._data.is_empty():
            return
        self._data = BM25(self.file_path)
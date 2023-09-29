#!/usr/bin/env python3
# -*-coding:utf-8-*-

import json
import string
import asyncio
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Set
import heapq
import concurrent.futures

from loguru import logger
import jieba
from nltk.text import TextCollection

from .base import DB


@dataclass
class BM25Data:
    file_path: str
    texts: List[str] = field(default_factory=list)
    stop_words: Set[str] = field(init=False)
    preprocessed_texts: List[str] = field(default_factory=list)
    text_collection: TextCollection = field(init=False)
    tf_idf_values: dict = field(default_factory=dict)
    tf_values: dict = field(default_factory=dict)
    word_sets: dict = field(default_factory=dict)
    text_lens: dict = field(default_factory=dict)
    sum_len: float = field(init=False, default=0)

    def __post_init__(self):
        self.stop_words = set(
            line.strip() for line in
            Path('sources/baidu_stopwords.txt').read_text(encoding='utf-8').splitlines()
        )
        for text in list(self.texts):
            self.add(text)

    def preprocess_text(self, text: str) -> str:
        words = jieba.cut(text)
        words = [
            word for word in words
            if word not in self.stop_words and word not in string.punctuation
        ]
        return ' '.join(words)

    def add(self, text: str):
        self.texts.append(text)
        preprocessed_text = self.preprocess_text(text)
        self.preprocessed_texts.append(preprocessed_text)
        self.text_collection = TextCollection(self.preprocessed_texts)
        self.sum_len += len(preprocessed_text.split())
        self.word_sets[text] = set(preprocessed_text.split())
        self.text_lens[text] = len(preprocessed_text.split())
        for word in self.word_sets[text]:
            key = f"{word}_{text}"
            self.tf_idf_values[key] = self.text_collection.tf_idf(word, text)
            self.tf_values[key] = self.text_collection.tf(word, text)
        if self.file_path:
            asyncio.run(self._save())

    async def _save(self):
        text_collection = self.text_collection
        del self.text_collection
        self.stop_words = list(self.stop_words) # type: ignore
        self.word_sets = {k: list(v) for k, v in self.word_sets.items()}
        with open(self.file_path, 'w') as f:
            json.dump(self.__dict__, f)
        self.text_collection = text_collection
        self.stop_words = set(self.stop_words)
        self.word_sets = {k: set(v) for k, v in self.word_sets.items()}

    @classmethod
    def load(cls, file_path: str):
        with open(file_path, 'r') as f:
            data = json.load(f)
        data['stop_words'] = set(data['stop_words'])
        data['word_sets'] = {k: set(v) for k, v in data['word_sets'].items()}
        instance = cls(file_path, **data)
        instance.text_collection = TextCollection(instance.preprocessed_texts)
        return instance

    def is_empty(self):
        return len(self.texts) == 0


@dataclass
class BM25(DB):
    file_path: str
    k1: float = 1.5
    b: float = 0.75
    _data: BM25Data = field(init=False)

    def __post_init__(self):
        if self.file_path and Path(self.file_path).exists():
            try:
                self._data = BM25Data.load(self.file_path)
            except:  # TODO: 无法导入也有可能可被修复，所以这里还需要更多的判断。
                self.init()
        else:
            self.init()

    def calculate_bm25_score(self, text: str, query: str) -> float:
        score = 0
        preprocessed_query = self._data.preprocess_text(query)
        for word in preprocessed_query.split():
            if word not in self._data.word_sets[text]:
                continue
            key = f"{word}_{text}"
            tf_idf_value = self._data.tf_idf_values.get(key, 0)
            tf_value = self._data.tf_values.get(key, 1e-9)
            text_len = self._data.text_lens[text]
            avg_len = self._data.sum_len / len(self._data.preprocessed_texts) if self._data.preprocessed_texts else 1
            score_part = (
                (self.k1 + 1) /
                (tf_value + self.k1 * (1 - self.b + self.b * text_len / avg_len))
            )
            score += tf_idf_value * score_part
        return score

    def search(self, query: str, n: int = DB.default_n) -> List[str]:
        if not query or self._data.is_empty():
            return []

        with concurrent.futures.ThreadPoolExecutor() as executor:
            scores = list(executor.map(self.calculate_bm25_score, self._data.texts, [query] * len(self._data.texts)))
        scores = list(zip(self._data.texts, scores))
        top_n_scores = heapq.nlargest(n, scores, key=lambda x: x[1])
        return [text for text, _ in top_n_scores]

    def add(self, text: str):
        self._data.add(text)

    def init(self):
        if hasattr(self, '_data') and self._data and self._data.is_empty():
            return
        self._data = BM25Data(self.file_path)
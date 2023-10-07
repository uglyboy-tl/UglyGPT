
import string
from pathlib import Path
from typing import List

import jieba.posseg as pseg

stop_words = set(
    line.strip() for line in
    Path("resource/baidu_stopwords.txt").read_text(encoding='utf-8').splitlines()
)
punt_list = set(['?', '!', ';', '？', '！', '。', '；', '……', '…', '\n'])
allow_speech_tags = set(['an', 'i', 'j', 'l', 'n', 'nr', 'nrfg', 'ns', 'nt', 'nz', 't', 'v', 'vd', 'vn', 'eng'])

def segment(text: str) -> str:
    # 结巴分词
    jieba_result = pseg.cut(text)
    # 词性筛选
    jieba_result = [w for w in jieba_result if w.flag in allow_speech_tags]
    # 去除特殊符号
    words = [w.word.strip() for w in jieba_result if w.flag!='x']
    # 去除停用词
    words = [
        word for word in words
        if word not in stop_words and word not in string.punctuation and len(word)>1
    ]
    # 英文
    words = [word.lower() for word in words]

    return ' '.join(words)

def cut_sentences(text: str) -> List[str]:
    """
    Split the text into sentences.
    """
    sentences = [text]
    for sep in punt_list:
        text_list, sentences = sentences, []
        for seq in text_list:
            sentences += seq.split(sep)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 0]
    return sentences

import logging
import os
import sys

from llama_index.core import (
    StorageContext,
    SummaryIndex,
    load_index_from_storage,
)
from llama_index.readers.github import GithubRepositoryReader
from uglychain.llm.llama_index import LlamaIndexLLM
from uglychain import Model
from uglygpt.utils.config import config
import nest_asyncio

nest_asyncio.apply()
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))


# load the documents and create the index
owner = "rjmacarthy"
repo = "twinny"
branch = "master"
# check if storage already exists
PERSIST_DIR = "./data/github/" + owner + "/" + repo
if not os.path.exists(PERSIST_DIR):
    documents = GithubRepositoryReader(
        github_token=config.github_token,
        owner=owner,
        repo=repo,
        use_parser=False,
        verbose=False,
        ignore_directories=["examples"],
    ).load_data(branch=branch)
    index = SummaryIndex.from_documents(documents, show_progress=True, build_tree=True)
    # store it for later
    index.storage_context.persist(persist_dir=PERSIST_DIR)
else:
    # load the existing index
    storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
    index = load_index_from_storage(storage_context)

query_engine = index.as_query_engine(
    llm = LlamaIndexLLM(model = Model.YI),
    retriever_mode="all_leaf",
    response_mode='tree_summarize',
)
response = query_engine.query("这个项目是如何实现补全功能的？给我看一看具体的代码。")
print(response)
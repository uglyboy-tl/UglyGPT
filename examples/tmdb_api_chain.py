from uglygpt.base import config, logger, Fore
from uglygpt.provider import get_llm_provider
from uglygpt.chains.api_chain.tmdb_docs import TMDB_DOCS
from uglygpt.chains.api_chain.base import APIChain
headers = {"Authorization": f"Bearer {config.tmdb_api_key}"}
chain = APIChain.from_llm_and_api_docs(llm=get_llm_provider(), api_docs=TMDB_DOCS, headers=headers)
logger.info(chain.run("我想找找2000年最热门的动作电影，只看第一页结果, 要中文的"),"最终结果", Fore.MAGENTA)
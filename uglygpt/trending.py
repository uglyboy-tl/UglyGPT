from uglygpt.obsidian import GithubTrending
from uglychain import Model

def trending():
    trending = GithubTrending(model=Model.GPT3_TURBO)
    trending.output_markdown()
    trending.feishu_output()

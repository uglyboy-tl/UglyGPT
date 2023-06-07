import re

def get_content_between_a_b(a,b,text):
    return re.search(f"{a}(.*?)\n{b}", text, re.DOTALL).group(1).strip()

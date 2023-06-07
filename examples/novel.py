from uglygpt.chains.novel.base import NovelChain
from uglygpt.base import config

def parse_instructions(instructions):
    output = ""
    for i in range(len(instructions)):
        output += f"{i+1}. {instructions[i]}\n"
    return output

config.set_debug_mode(True)

chain = NovelChain()
chain.set_type("init")
output = chain({"type":"科幻", "topic":"虫族"})
chain.set_type("novel")

previous_paragraph = "\n".join([output['Paragraph 1'], output['Paragraph 2']])
writer_new_paragraph = output['Paragraph 3']
memory = output['Summary']
user_edited_plan = [output['Instruction 1'],output['Instruction 2'],output['Instruction 3']]

output = chain({"previous_paragraph":previous_paragraph, "writer_new_paragraph":writer_new_paragraph, "memory":memory, "user_edited_plan":user_edited_plan})
#print(output)

chain.set_type("plan")
previous_plans = parse_instructions(user_edited_plan)

output = chain({"previous_paragraph":previous_paragraph,"memory":memory,"previous_plans":previous_plans, "writer_new_paragraph":writer_new_paragraph})

print(output)
user_edited_plan = output['Selected Plan']
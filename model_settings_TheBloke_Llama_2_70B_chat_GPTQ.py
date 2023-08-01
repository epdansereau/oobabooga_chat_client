def context_instruct(context):
    return f'''[INST] <<SYS>>
{context}
<</SYS>>

'''

model_settings = {
    'mode': 'instruct',  # Valid options: 'chat', 'chat-instruct', 'instruct'. We use instruct mode even though we're chatting.
    'character': '',
    'instruction_template': 'LLama-V2',  # Will get autodetected if unset
    'chat_instruct_command': '<|prompt|>',
    'your_name': '',
}
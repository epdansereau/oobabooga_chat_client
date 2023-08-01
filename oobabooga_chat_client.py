# Adapted from https://github.com/oobabooga/text-generation-webui/blob/main/api-examples/api-example-chat-stream.py
import asyncio
import json
import sys

try:
    import websockets
except ImportError:
    print("Websockets package not found. Make sure it's installed.")

from model_settings_TheBloke_Llama_2_70B_chat_GPTQ import model_settings, context_instruct
from task_settings_inference_defaults import task_settings

# For local streaming, the websockets are hosted without ssl - ws://
HOST = 'localhost:5005'
URI = f'ws://{HOST}/api/v1/chat-stream'

# For reverse-proxied streaming, the remote will likely host with ssl - wss://
# URI = 'wss://your-uri-here.trycloudflare.com/api/v1/stream'


async def run(user_input, history, context_system):
    # Note: the selected defaults change from time to time.
    request = {
        'user_input': user_input,
        'max_new_tokens': 250,
        'history': history,
        'context_instruct': context_instruct(context_system),
        **model_settings,
        **task_settings
    }

    async with websockets.connect(URI, ping_interval=None) as websocket:
        await websocket.send(json.dumps(request))

        while True:
            incoming_data = await websocket.recv()
            incoming_data = json.loads(incoming_data)

            match incoming_data['event']:
                case 'text_stream':
                    yield incoming_data['history']
                case 'stream_end':
                    return


async def print_response_stream(user_input, history, context_system):
    async for cur_message, new_history, response in stream(user_input, history, context_system):
        print(cur_message, end='')
        sys.stdout.flush()  # If we don't flush, we won't see tokens in realtime.
    print()
    return new_history, response

async def stream(user_input, history, context_system):
    cur_len = 0
    response = ''
    async for new_history in run(user_input, history, context_system):
        cur_message = new_history['visible'][-1][1][cur_len:]
        cur_len += len(cur_message)
        response += cur_message
        yield cur_message, new_history, response

async def stream_block(user_input, history, context_system):
    cur_len = 0
    response = ''
    async for new_history in run(user_input, history, context_system):
        cur_message = new_history['visible'][-1][1][cur_len:]
        cur_len += len(cur_message)
        response += cur_message
    return response, new_history


def command_line_interface():
    # Basic example
    history = {'internal': [], 'visible': []}
    context_system = 'Answer the questions.'

    default_user_input = "Tell me a joke, then explain it."
    block = False

    while True:
        user_input = input('Prompt: ')
        if user_input == '':
            user_input = default_user_input
        if user_input == 'q':
            break
        if user_input == 'r':
            history = {'internal': [], 'visible': []}
            continue
        if user_input == 'sy':
            context_system = input('System command: ')
            continue
        if user_input == 'b':
            block = not block
            continue
        if block:
            response, history = asyncio.run(stream_block(user_input, history, context_system))
            print(response)
        else:
            history, _ = asyncio.run(print_response_stream(user_input, history, context_system))


if __name__ == '__main__':

    command_line_interface()

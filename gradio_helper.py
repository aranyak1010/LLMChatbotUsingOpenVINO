from typing import Callable, Literal
import gradio as gr  # Fixed import
from uuid import uuid4

english_examples = [
    ["Hello there! How are you doing?"],
    ["What is OpenVINO?"],
    ["Who are you?"],
    ["Can you explain to me briefly what is Python programming language?"],
    ["Explain the plot of Cinderella in a sentence."],
    ["What are some common mistakes to avoid when writing code?"],
    ["Write a 100-word blog post on 'Benefits of Artificial Intelligence and OpenVINO'"],
]

def get_uuid():
    """
    Generate a universal unique identifier for the thread.
    """
    return str(uuid4())

def handle_user_message(message, history):
    """
    Callback function to update user messages in the interface upon submit button click.

    Params:
      message (str): The current user message.
      history (list): Conversation history.

    Returns:
      tuple: Updated message box (empty) and conversation history with new user input.
    """
    return "", history + [[message, ""]]

def make_demo(run_fn: Callable, stop_fn: Callable, title: str = "OpenVINO Chatbot", language: Literal["English", "Chinese", "Japanese"] = "English"):
    examples = english_examples

    with gr.Blocks(
        theme=gr.themes.Soft(),
        css=".disclaimer {font-variant-caps: all-small-caps;}",
    ) as demo:
        conversation_id = gr.State(get_uuid())  # Fixed state initialization
        gr.Markdown(f"<h1><center>{title}</center></h1>")
        
        chatbot = gr.Chatbot(height=500)
        
        with gr.Row():
            msg = gr.Textbox(
                label="Chat Message Box",
                placeholder="Type your message here...",
                show_label=False,
                container=False,
            )
            submit = gr.Button("Submit")
            stop = gr.Button("Stop")
            clear = gr.Button("Clear")

        with gr.Accordion("Advanced Options:", open=False):
            with gr.Row():
                temperature = gr.Slider(
                    label="Temperature",
                    value=0.1,
                    minimum=0.0,
                    maximum=1.0,
                    step=0.1,
                    interactive=True,
                    info="Higher values produce more diverse outputs",
                )
                top_p = gr.Slider(
                    label="Top-p (nucleus sampling)",
                    value=1.0,
                    minimum=0.0,
                    maximum=1.0,
                    step=0.01,
                    interactive=True,
                    info="Sample from the smallest possible set of tokens whose cumulative probability exceeds top_p.",
                )
                top_k = gr.Slider(
                    label="Top-k",
                    value=50,
                    minimum=0.0,
                    maximum=200,
                    step=1,
                    interactive=True,
                    info="Sample from a shortlist of top-k tokens — 0 to disable.",
                )
                repetition_penalty = gr.Slider(
                    label="Repetition Penalty",
                    value=1.1,
                    minimum=1.0,
                    maximum=2.0,
                    step=0.1,
                    interactive=True,
                    info="Penalize repetition — 1.0 to disable.",
                )

        gr.Examples(examples, inputs=msg, label="Click on an example and press 'Submit'")

        submit_event = msg.submit(
            fn=handle_user_message,
            inputs=[msg, chatbot],
            outputs=[msg, chatbot],
            queue=False,
        ).then(
            fn=run_fn,
            inputs=[chatbot, temperature, top_p, top_k, repetition_penalty, conversation_id],
            outputs=chatbot,
            queue=True,
        )

        submit_click_event = submit.click(
            fn=handle_user_message,
            inputs=[msg, chatbot],
            outputs=[msg, chatbot],
            queue=False,
        ).then(
            fn=run_fn,
            inputs=[chatbot, temperature, top_p, top_k, repetition_penalty, conversation_id],
            outputs=chatbot,
            queue=True,
        )

        stop.click(
            fn=stop_fn,
            inputs=None,
            outputs=None,
            cancels=[submit_event, submit_click_event],
            queue=False,
        )

        clear.click(
            lambda: ("", []),  # Reset input and chatbot history
            None,
            [msg, chatbot],
            queue=False,
        )

    return demo

from typing import Dict

def wrap_prompt(base_prompt: str, expected_format: Dict, system_context: str = None) -> str:
    """
    Wraps a prompt with clear instructions about response format and single-turn interaction.
    
    Args:
        base_prompt: The core prompt/question for the LLM
        expected_format: Dictionary showing the expected response structure
        system_context: Optional system context to set the stage
    """
    format_example = "\n".join([
        f"{key}: <{value}>" for key, value in expected_format.items()
    ])
    
    wrapper = [
        "IMPORTANT INSTRUCTIONS:",
        "1. Respond ONLY with the requested format below",
        "2. Do NOT include explanations or additional text",
        "3. Do NOT wait for confirmation or further input",
        "4. Ensure ALL required fields are present",
        "\nEXPECTED FORMAT:",
        format_example,
        "\nPROMPT:"
    ]
    
    if system_context:
        wrapper.insert(0, f"CONTEXT: {system_context}\n")
    
    return "\n".join(wrapper + [base_prompt])
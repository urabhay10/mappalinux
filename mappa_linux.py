import sys
import os
import json
import subprocess
import getpass
from google import genai
from google.genai import types, errors

def get_sudo_password():
    return getpass.getpass("sudo password: ")

def execute_command(command, sudo_password=None):
    if command.strip().startswith("sudo") and sudo_password:
        cmd_exec = command.replace("sudo", "sudo -S", 1)
        try:
            result = subprocess.run(
                cmd_exec,
                input=sudo_password + "\n",
                shell=True,
                capture_output=True,
                text=True
            )
            return result.stdout + result.stderr
        except Exception as e:
            return str(e)
    else:
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True
            )
            return result.stdout + result.stderr
        except Exception as e:
            return str(e)

def main():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        try:
            api_key = getpass.getpass("Gemini API Key: ")
        except KeyboardInterrupt:
            sys.exit(1)
            
    if not api_key:
        print("Error: API key is required.")
        sys.exit(1)

    client = genai.Client(api_key=api_key)

    if len(sys.argv) < 2:
        try:
            user_input = input("Request: ")
        except KeyboardInterrupt:
            sys.exit(0)
    else:
        user_input = " ".join(sys.argv[1:])

    if not user_input.strip():
        sys.exit(0)

    sudo_password = None

    response_schema = {
        "type": "OBJECT",
        "required": ["message", "commands", "done_bit"],
        "properties": {
            "message": {"type": "STRING"},
            "commands": {
                "type": "ARRAY",
                "items": {"type": "STRING"},
            },
            "done_bit": {"type": "BOOLEAN"},
        },
    }

    config = types.GenerateContentConfig(
        response_mime_type='application/json',
        response_schema=response_schema,
        safety_settings=[
            types.SafetySetting(category='HARM_CATEGORY_HATE_SPEECH', threshold='BLOCK_NONE'),
            types.SafetySetting(category='HARM_CATEGORY_DANGEROUS_CONTENT', threshold='BLOCK_NONE'),
            types.SafetySetting(category='HARM_CATEGORY_HARASSMENT', threshold='BLOCK_NONE'),
            types.SafetySetting(category='HARM_CATEGORY_SEXUALLY_EXPLICIT', threshold='BLOCK_NONE'),
        ]
    )

    chat = client.chats.create(
        model='gemini-2.5-flash',
        config=config
    )
    
    system_instruction = """You are a Linux terminal assistant.
    
    Output structured JSON:
    {
        "message": "Description of action or result.",
        "commands": ["cmd1", "cmd2"],
        "done_bit": true 
    }
    
    1. If tasks remain, set "done_bit": false and list "commands".
    2. If finished, set "done_bit": true and leave "commands" empty.
    3. Use command outputs to guide next steps.
    """
    
    # Initialize conversation
    current_prompt = f"{system_instruction}\n\nTask: {user_input}"
    
    while True:
        try:
            response = chat.send_message(current_prompt)
            text = response.text.replace("```json", "").replace("```", "").strip()
            
            try:
                data = json.loads(text)
            except json.JSONDecodeError:
                print(f"Error: Invalid JSON response.\n{text}")
                break
                
            message = data.get("message", "")
            commands = data.get("commands", [])
            done_bit = data.get("done_bit", False)
            
            if message:
                print(f"> {message}")
            
            if done_bit and not commands:
                break
            
            command_outputs = []
            for cmd in commands:
                print(f"$ {cmd}")
                if cmd.strip().startswith("sudo") and sudo_password is None:
                    sudo_password = get_sudo_password()
                
                output = execute_command(cmd, sudo_password)
                if output.strip():
                    print(output.strip())
                command_outputs.append(f"CMD: {cmd}\nOUT:\n{output}")
            
            if done_bit:
                break
            
            execution_log = "\n".join(command_outputs)
            current_prompt = f"Results:\n{execution_log}\n\nContinue or finish."
            
        except errors.APIError as e:
            print(f"API Error: {e.message}")
            break
        except Exception as e:
            print(f"Error: {e}")
            break

if __name__ == "__main__":
    main()

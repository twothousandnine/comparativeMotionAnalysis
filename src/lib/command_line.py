from    src.lib.error import *
import  subprocess
import  os

def bash_prompt(command: str) -> str:
    if not command:
        raise Error("Empty prompt used")

    try:
        result = os.popen(command)
        lines = result.readlines()
        lines = [line[:-1] for line in lines]
        retstring = "\n".join(lines)
        result.close()

        return retstring
    except subprocess.CalledProcessError as e:
        raise Error(f"Command '{command}' failed: {e.stderr}") from None

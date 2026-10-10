import time
import json

# task executor
def task_executor(job,payload):
    if job.type == "sleep":
        seconds = int(payload["seconds"])

        result = sleep_handler(seconds)
        job.result = result
        return result

    elif job.type == "calculation":
        first = payload["first"]
        second = payload["second"]
        operator = payload["operator"]

        result = calculation_handler(first,second,operator)
        job.result = result
        return result

    else:
        raise TypeError("Invalid Job Type Received")

# Calculation handler
def calculation_handler(first:str,second:str,operator:str):
    if operator == "+":
        result = int(first) + int(second)
    elif operator == "-":
        result = int(first) - int(second)
    elif operator == "*":
        result = int(first) * int(second)
    elif operator == "/":
        result = int(first) / int(second)
    elif operator == "//":
        result = int(first) // int(second)
    elif operator == "**":
        result = int(first) ** int(second)
    else:
        raise ValueError(f"Unsupported Operator")

    return json.dumps({
        "result": str(result)
    })

# Sleep handler
def sleep_handler(seconds:str):
    time.sleep(seconds)

    return json.dumps({
        "result": f"Slept for {seconds}s"
    })
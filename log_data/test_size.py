import sys

# read ./responses.json
# reas example_logs.json

with open("./responses.json") as f:
    responses = f.read()
    print(sys.getsizeof(responses) / 1_000_000, "MB")

with open("./example_logs.json") as f:
    log_data = f.read()
    print(sys.getsizeof(log_data) / 1_000_000, "MB")

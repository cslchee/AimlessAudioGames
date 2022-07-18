import io
import json

def getLocalJsonData(filename: str) -> dict:
    if not filename.endswith('.json'):
        filename += '.json'
    resp: io.StringIO = pyodide.open_url(f'http://127.0.0.1:8887/{filename}')
    return json.loads(resp.read())


def main():
    pass


try:
    main()
except Exception as e:
    print(f"Error starting main() - Error: {e}")

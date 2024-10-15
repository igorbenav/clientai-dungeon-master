import subprocess
import time
import requests
import logging

logging.basicConfig(level=logging.INFO)

def start_ollama_server(timeout: int = 30, check_interval: float = 1.0):
    """
    Start the Ollama server and wait for it to be ready.
    """
    logging.info("Starting Ollama server...")

    try:
        process = subprocess.Popen(
            ['ollama', 'serve'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
    except subprocess.SubprocessError as e:
        logging.error(f"Failed to start Ollama process: {e}")
        raise

    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get('http://localhost:11434', timeout=5)
            if response.status_code == 200:
                logging.info("Ollama server is ready.")
                return process
        except requests.ConnectionError:
            pass
        except requests.RequestException as e:
            logging.error(f"Unexpected error when checking Ollama server: {e}")
            process.terminate()
            raise

        if process.poll() is not None:
            stdout, stderr = process.communicate()
            logging.error(f"Ollama process terminated unexpectedly. stdout: {stdout}, stderr: {stderr}")
            raise subprocess.SubprocessError("Ollama process terminated unexpectedly")

        time.sleep(check_interval)

    process.terminate()
    raise TimeoutError(f"Ollama server did not start within {timeout} seconds")

from game.dungeon_master import EnhancedAIDungeonMaster
from utils.text_utils import print_slowly
from ai.ollama_server import start_ollama_server

def main():
    print_slowly("Welcome to the AI Dungeon Master!")
    print_slowly("Prepare for an adventure guided by multiple AI models.")
    print_slowly("Type 'quit' at any time to exit the game.")
    print()

    # Start the Ollama server before the game begins
    ollama_process = start_ollama_server()

    game = EnhancedAIDungeonMaster()
    game.play_game()

    print_slowly("Thank you for playing AI Dungeon Master!")

    # Terminate the Ollama server when the game ends
    if ollama_process:
        ollama_process.terminate()

if __name__ == "__main__":
    main()

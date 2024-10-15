from typing import Tuple, List
import random
import time

from ai.ai_providers import AIProviders
from utils.text_utils import print_separator
from game.character import Character
from game.game_state import GameState

class EnhancedAIDungeonMaster:
    def __init__(self):
        self.ai = AIProviders()
        self.conversation_history = []
        self.game_state = None

    def create_character(self):
        print("Let's create your character!")
        name = input("What is your character's name? ")
        
        character_prompt = f"""
        Create a character for a fantasy RPG with the following details:
        Name: {name}
        
        Please provide:
        1. A suitable race (e.g., Human, Elf, Dwarf, etc.)
        2. A class (e.g., Warrior, Mage, Rogue, etc.)
        3. A brief background story (2-3 sentences)
        4. Basic stats (Strength, Dexterity, Constitution, Intelligence, Wisdom, Charisma) on a scale of 1-20
        
        Format the response as follows:
        Race: [race]
        Class: [class]
        Background: [background story]
        Stats:
        - Strength: [value]
        - Dexterity: [value]
        - Constitution: [value]
        - Intelligence: [value]
        - Wisdom: [value]
        - Charisma: [value]
        """
        
        self.add_to_history("user", character_prompt)
        character_info = self.print_stream(self.ai.chat(self.conversation_history, provider='openai'))
        
        # Parse the character info
        lines = character_info.strip().split('\n')
        race = class_type = background = ""
        stats = {}
        
        for line in lines:
            if line.startswith("Race:"):
                race = line.split(": ", 1)[1].strip()
            elif line.startswith("Class:"):
                class_type = line.split(": ", 1)[1].strip()
            elif line.startswith("Background:"):
                background = line.split(": ", 1)[1].strip()
            elif ":" in line and not line.startswith("Stats:"):
                key, value = line.split(":", 1)
                key = key.strip("- ")
                try:
                    stats[key] = int(value.strip())
                except ValueError:
                    stats[key] = random.randint(1, 20)
        
        # If any stat is missing, assign a random value
        for stat in ["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"]:
            if stat not in stats:
                stats[stat] = random.randint(1, 20)
        
        # If race, class, or background is empty, assign default values
        race = race or "Human"
        class_type = class_type or "Adventurer"
        background = background or "A mysterious traveler with an unknown past."
        
        return Character(name, race, class_type, background, stats)

    def add_to_history(self, role: str, content: str):
        # Only add to history if it's not a duplicate of the last message
        if not self.conversation_history or self.conversation_history[-1]['content'] != content:
            self.conversation_history.append({"role": role, "content": content})
            # Keep the conversation history to a reasonable size
            if len(self.conversation_history) > 10:
                self.conversation_history = self.conversation_history[-10:]

    def generate_environment(self):
        if not hasattr(self, 'current_environment'):
            prompt = f"""
            The character {self.game_state.character.name} is a {self.game_state.character.race} {self.game_state.character.class_type} 
            currently in the {self.game_state.location}.

            Describe the current environment in detail, focusing on:
            1. The physical setting and atmosphere
            2. Any notable NPCs present
            3. Interesting objects or features

            Do not create a new character or change any existing character details.
            Do not include any actions or dialogue for {self.game_state.character.name}.

            End your description with one of these tags if appropriate:
            [INTERACT_OPPORTUNITY] - if there's a chance for the player to interact with someone or something
            [QUEST_OPPORTUNITY] - if there's a potential quest or mission available
            """
            self.add_to_history("user", prompt)
            self.current_environment = self.ai.chat(self.conversation_history, provider='openai')
        return self.current_environment

    def handle_player_action(self, action):
        prompt = f"""
        The player ({self.game_state.character.name}, a {self.game_state.character.race} {self.game_state.character.class_type}) 
        attempts to {action} in {self.game_state.location}. 
        Describe the immediate result of this action, focusing on the environment and NPCs' reactions.
        Do not generate any further actions or dialogue for the player.
        If the player is trying to interact with an NPC, end your response with [NPC_INTERACTION: <npc_name>].
        """
        self.add_to_history("user", prompt)
        return self.ai.chat(self.conversation_history, provider='openai')

    def generate_npc_dialogue(self, npc_name: str, player_input: str):
        prompt = f"""
        The player ({self.game_state.character.name}) said to {npc_name}: "{player_input}"
        Generate a single, natural response from {npc_name}, addressing the player's input directly.
        If the player is asking about items for sale, list 2-3 specific items with brief descriptions and prices.
        Do not include any actions or responses from the player character.
        Keep the response concise and relevant to the player's input.
        Do not include any formatting tags, headers, or quotation marks in your response.
        Respond as if you are {npc_name} speaking directly to the player.
        """
        self.add_to_history("user", prompt)
        return self.ai.chat(self.conversation_history, provider='replicate')

    def generate_quest(self):
        prompt = f"""
        Generate a new quest opportunity for {self.game_state.character.name}, 
        a {self.game_state.character.race} {self.game_state.character.class_type}, 
        in {self.game_state.location}. 
        Present it as an opportunity, not a forced quest.
        The quest should be relevant to the current location and game state.
        """
        self.add_to_history("user", prompt)
        return self.ai.chat(self.conversation_history, provider='openai')

    def play_game(self):
        print("Welcome to the Dungeon!")
        character = self.create_character()
        self.game_state = GameState(character)
        
        print("\nYour adventure begins...")
        while True:
            print_separator()
            environment_description, env_flags = self.process_story(self.generate_environment())
            
            if "INTERACT_OPPORTUNITY" in env_flags:
                print("\nThere seems to be an opportunity to interact.")
            if "QUEST_OPPORTUNITY" in env_flags:
                print("\nThere might be a quest available.")
            
            action = input("\nWhat do you do? ")
            if action.lower() == "quit":
                break
            
            print("\nOutcome:")
            outcome, npc_interaction = self.process_story(self.handle_player_action(action))
            
            self.update_game_state(outcome)
            
            if npc_interaction:
                self.handle_conversation(npc_interaction)
            
            print_separator()
            print(f"Current state: {str(self.game_state)}")
            
            if self.game_state.health <= 0:
                print("Game Over! Your health reached 0.")
                break
            
            if hasattr(self, 'current_environment'):
                del self.current_environment

    def handle_conversation(self, npc_name):
        print(f"\nYou are now in conversation with {npc_name}.")
        self.conversation_history = [
            {"role": "system", "content": f"You are {npc_name}, speaking directly to the player. Respond naturally and in character."}
        ]
        while True:
            player_input = input(f"\nWhat do you say to {npc_name}? (or type 'end conversation' to stop): ")
            if player_input.lower() == "end conversation":
                print(f"\nYou end your conversation with {npc_name}.")
                break
            
            print(f"\n{npc_name}:")
            self.print_stream(self.generate_npc_dialogue(npc_name, player_input))

    def process_story(self, story_generator) -> Tuple[str, List[str]]:
        story = self.print_stream(story_generator, print_output=True)
        story_lines = story.split('\n')
        
        flags = []
        for line in reversed(story_lines):
            if line.strip().startswith('[') and line.strip().endswith(']'):
                flags.append(line.strip('[').strip(']'))
                story_lines.remove(line)
            else:
                break
        
        story_content = '\n'.join(story_lines).strip()
        
        if any(flag.startswith("NPC_INTERACTION:") for flag in flags):
            npc_name = next(flag.split(':')[1].strip() for flag in flags if flag.startswith("NPC_INTERACTION:"))
            return story_content, npc_name
        else:
            return story_content, flags

    def update_game_state(self, outcome):
        if "found" in outcome.lower():
            item = outcome.split("found")[1].split(".")[0].strip()
            self.game_state.update(item=item)
        if "new area" in outcome.lower():
            new_location = outcome.split("new area")[1].split(".")[0].strip()
            self.game_state.update(location=new_location)
        if "damage" in outcome.lower():
            self.game_state.update(health_change=-10)
        if "healed" in outcome.lower():
            self.game_state.update(health_change=10)
        if "quest" in outcome.lower():
            quest = outcome.split("quest")[1].split(".")[0].strip()
            self.game_state.update(quest=quest)
        self.game_state.update(exp_gain=5)

    def print_stream(self, stream, print_output=True) -> str:
        full_text = ""
        for chunk in stream:
            if print_output:
                print(chunk, end='', flush=True)
            full_text += chunk
            time.sleep(0.03)
        if print_output:
            print()
        return full_text

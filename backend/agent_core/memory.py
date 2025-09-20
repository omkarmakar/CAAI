from typing import List, Dict, Any

class MemoryModule:
    """
    Manages the short-term and long-term memory of the agent.
    """
    def __init__(self):
        self.short_term_memory: List[Dict[str, Any]] = []
        # In a real application, this would be a connection to a vector database
        # like Pinecone, Weaviate, or FAISS.
        self.long_term_memory: Dict[str, Any] = {}

    def add_to_short_term(self, interaction: Dict[str, Any]):
        """
        Adds an interaction to the short-term memory.

        Args:
            interaction (Dict[str, Any]): The interaction to add.
        """
        self.short_term_memory.append(interaction)

    def get_short_term_context(self) -> List[Dict[str, Any]]:
        """
        Retrieves the current short-term memory context.

        Returns:
            List[Dict[str, Any]]: The list of recent interactions.
        """
        return self.short_term_memory

    def store_in_long_term(self, key: str, data: Any):
        """
        Stores data in the long-term memory.

        Args:
            key (str): The key to store the data under.
            data (Any): The data to store.
        """
        self.long_term_memory[key] = data

    def retrieve_from_long_term(self, key: str) -> Any:
        """
        Retrieves data from the long-term memory.

        Args:
            key (str): The key of the data to retrieve.

        Returns:
            Any: The retrieved data, or None if not found.
        """
        return self.long_term_memory.get(key)
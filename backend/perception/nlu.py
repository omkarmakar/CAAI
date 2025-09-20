from transformers import pipeline

class NaturalLanguageUnderstanding:
    """
    Handles natural language understanding using a pre-trained model.
    """
    def __init__(self, model_name="distilbert-base-uncased-finetuned-sst-2-english"):
        """
        Initializes the NLU pipeline.
        """
        self.nlp = pipeline("sentiment-analysis", model=model_name)

    def interpret_query(self, query: str) -> dict:
        """
        Interprets the user's query to understand intent and sentiment.

        Args:
            query (str): The natural language query from the user.

        Returns:
            dict: A dictionary containing the interpreted intent and sentiment.
        """
        # In a real-world scenario, this would involve more sophisticated
        # intent recognition and entity extraction.
        # For this example, we'll just analyze the sentiment.
        result = self.nlp(query)
        return {
            "query": query,
            "sentiment": result[0]['label'],
            "confidence": result[0]['score']
        }
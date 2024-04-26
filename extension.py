from abc import ABC

class ExtensionInterface(ABC):

    def call(self, prompt: str) -> str:
        """Modify prompt during inference"""
        pass

    def check_for_trigger(self, prompt: str) -> bool:
        """Check if prompt triggers the extension"""
        pass

    def modify_prompt_for_llm(self, prompt: str, results: str, user: str) -> str:
        """Modify prompt before llm inference"""
        pass

    def modify_response_for_user(self, results: str, user: str) -> str:
        """Modify response before sending to user (if no llm available)"""
        pass
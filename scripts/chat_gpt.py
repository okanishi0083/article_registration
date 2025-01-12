import requests


class CustomGPTClient:
    """
    A client for interacting with a custom GPT project using OpenAI's API.
    """

    def __init__(
        self,
        api_key,
        custom_gpt_id,
        system_message_generator,
        edit_user_input,
        temperature_generator,
    ):
        """
        Initializes the client with an API key, custom GPT ID, and external generators.

        Args:
            api_key (str): API key for authenticating with OpenAI API.
            custom_gpt_id (str): ID of the custom GPT project.
            system_message_generator (callable): Function to generate the system message.
            temperature_generator (callable): Function to generate the temperature value.
        """
        if not api_key or not custom_gpt_id:
            raise ValueError("API key and custom GPT ID are required.")
        self.api_key = api_key
        self.custom_gpt_id = custom_gpt_id
        self.system_message_generator = system_message_generator
        self.edit_user_input = edit_user_input
        self.temperature_generator = temperature_generator
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        self.url = "https://api.openai.com/v1/chat/completions"

    def send_message(self, tag_data, entry, context="precise"):
        """ """
        system_message = self.system_message_generator()
        user_message = self.edit_user_input(tag_data, entry)
        temperature = self.temperature_generator(context)

        data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message},
            ],
            "temperature": temperature,
            "max_tokens": 150,
        }

        try:
            response = requests.post(self.url, headers=self.headers, json=data)
            response.raise_for_status()
            response_json = response.json()
            return (
                response_json.get("choices", [])[0]
                .get("message", {})
                .get("content", "")
            )
        except requests.exceptions.RequestException as e:
            raise requests.exceptions.RequestException(f"API request failed: {e}")

from openai import AsyncOpenAI

from models.dbs.enums import *
from models.dbs.models import *
from models.dbs.orm import Orm


class OpenAI_API:
    SYSTEM_MESSAGE = """
    You are an advanced AI assistant designed to provide accurate, concise, and helpful responses. Your primary goal is to assist users with their queries by providing clear and relevant information. Follow these guidelines to maximize your efficiency:

    1. **Clarity and Conciseness**: Provide clear and concise answers. Avoid unnecessary details unless explicitly requested.
    2. **Accuracy**: Ensure that all information provided is accurate and up-to-date.
    3. **Relevance**: Stick to the topic of the query. Avoid deviating into unrelated subjects.
    4. **Politeness**: Maintain a polite and professional tone at all times.
    5. **Examples and Explanations**: When applicable, provide examples or explanations to clarify complex topics.
    6. **Step-by-Step Instructions**: For procedural queries, provide step-by-step instructions to guide the user.
    7. **Resourcefulness**: If a query requires external resources or references, mention them clearly.
    8. **Adaptability**: Adjust your responses based on the user's level of understanding and context provided in the query.

    Remember, your goal is to be as helpful and efficient as possible. If you are unsure about a query, provide the best possible answer based on the information available.
    """

    def __init__(self, user: User, system_message=SYSTEM_MESSAGE):
        self.user = user
        self.chat_model = user.chat_model
        self.image_model = user.image_model
        self.openai = AsyncOpenAI()
        self.system_message = system_message

    async def __call__(self, query):
        return await self.chatgpt(query)

    async def chatgpt(self, query):
        if await self.validate_request(self.chat_model.name):
            messages = await self.get_chat_messages(query)

            response = await self.openai.chat.completions.create(
                model=self.chat_model.value.lower(),
                messages=messages,
                max_tokens=4096
            )

            await Orm.add_context_message(self.user, query, "user")
            await Orm.add_context_message(self.user, response.choices[0].message.content, "assistant")

            answer = response.choices[0].message.content
            answers = await self.split_text(answer)
            return answers

        return None

    async def split_text(self, text, length=4095):
        parts = [text[i:i+length] for i in range(0, len(text), length)]
        return parts

    async def get_chat_messages(self, query):
        messages = await Orm.get_context_messages(self.user) + [
            {"role": "system", "content": self.system_message},
            {"role": "user", "content": query}
        ]
        return messages

    async def generate_image(self, query):
        if await self.validate_request(self.image_model.name):
            response = await self.openai.images.generate(
                model=self.image_model.value.lower(),
                prompt=query
            )

            return response.data[0].url
        return None

    async def validate_request(self, model: str):
        return True

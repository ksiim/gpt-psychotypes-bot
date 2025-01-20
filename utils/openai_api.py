from openai import AsyncOpenAI

from models.dbs.enums import *
from models.dbs.models import *
from models.dbs.orm import Orm


class OpenAI_API:
    SYSTEM_MESSAGE = ''

    def __init__(self, user: User, system_message=SYSTEM_MESSAGE):
        self.user = user
        self.chat_model = user.psychotype.chat_model
        self.image_model = user.image_model
        self.openai = AsyncOpenAI()
        self.system_message = system_message

    async def __call__(self, query):
        return await self.chatgpt(query)

    async def chatgpt(self, query):
        if not await self.validate_request(self.chat_model.name):
            return None
        
        psychotype = self.user.psychotype.name
        
        messages = await self.get_chat_messages(query, psychotype=psychotype)
        try:
            response = await self.openai.chat.completions.create(
                model=self.chat_model.value.lower(),
                messages=messages,
                max_tokens=4096
            )
        except Exception as e:
            if '429' in str(e):
                response = await self.openai.chat.completions.create(
                model=ChatModelEnum.GPT_4O_MINI.value.lower(),
                messages=messages,
                max_tokens=4096
            )
            else:
                return None

        await Orm.add_context_message(self.user, query, "user")
        await Orm.add_context_message(self.user, response.choices[0].message.content, "assistant")
        await self.update_limits(self.chat_model.name)
        await Orm.update_psychotype_statistic(psychotype)

        answer = response.choices[0].message.content
        answers = await self.split_text(answer)
        return answers

    async def split_text(self, text, length=4095):
        parts = [text[i:i+length] for i in range(0, len(text), length)]
        return parts
    
    async def update_limits(self, model):
        if "GPT" in model:
            await self.update_text_limit()
        elif "DALL" in model:
            await self.update_image_limit()
            
    async def update_text_limit(self):
        if self.user.bought_text_limits_count:
            await Orm.decrease_bought_text_usage_count(self.user.id)
        else:
            await Orm.decrease_free_text_usage_count(self.user.id)
            
    async def update_image_limit(self):
        if self.user.bought_image_limits_count:
            await Orm.decrease_bought_image_usage_count(self.user.id)
        else:
            await Orm.decrease_free_image_usage_count(self.user.id)
            

    async def get_chat_messages(self, query, psychotype):
        psychotype_prompt = (await Orm.get_psychotype_by_name(psychotype)).prompt
        messages = await Orm.get_context_messages(self.user, psychotype) + [
            {"role": "system", "content": psychotype_prompt},
            {"role": "user", "content": query}
        ]
        return messages

    async def generate_image(self, query):
        if await self.validate_request(self.image_model.name):
            response = await self.openai.images.generate(
                model=self.image_model.value.lower(),
                prompt=query
            )
            
            await self.update_limits(self.image_model.name)

            return response.data[0].url
        return None

    async def validate_request(self, model: str):
        limit = await self.get_limits(model)
        return limit > 0
    
    async def get_limits(self, model: str):
        if "GPT" in model:
            return await self.get_text_limit()
        elif "DALL" in model:
            return await self.get_image_limit()
        
    async def get_text_limit(self):
        if self.user.bought_text_limits_count:
            return self.user.bought_text_limits_count
        return self.user.free_text_limits_count
        
    async def get_image_limit(self):
        if self.user.bought_image_limits_count:
            return self.user.bought_image_limits_count
        return self.user.free_image_limits_count

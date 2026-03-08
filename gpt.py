import logging
from openai import AsyncOpenAI
from credentials import OPENAI_API_KEY


class ChatGptService:
    def __init__(self, token):
        self.client = AsyncOpenAI(api_key=token)
        self.message_list = []

    async def send_message_list(self) -> str:
        try:
            # Отримуємо відповідь від OpenAI
            completion = await self.client.chat.completions.create(
                model="gpt-4o-mini",  # Використовуємо 4o-mini для стабільності, якщо 5-mini глючить
                messages=self.message_list,
                max_completion_tokens=1000,
                temperature=1
            )

            # ВИПРАВЛЕНО: Отримуємо текст через атрибут .content
            if completion.choices and completion.choices[0].message.content:
                answer = completion.choices[0].message.content

                # Додаємо в історію як чистий словник
                self.message_list.append({"role": "assistant", "content": answer})
                return answer
            else:
                return "ШІ повернув порожню відповідь. Спробуйте ще раз."

        except Exception as e:
            import logging
            logging.error(f"GPT Error: {e}")
            return f"⚠️ Помилка ШІ: {e}"

    async def send_image_analysis(self, image_bytes: bytes, prompt: str) -> str:
        try:
            import base64
            base64_image = base64.b64encode(image_bytes).decode('utf-8')

            completion = await self.client.chat.completions.create(
                model="gpt-5-mini",  # або gpt-4o
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]
                }]
            )
            return completion.choices[0].message.content
        except Exception as e:
            return f"⚠️ Помилка аналізу фото: {e}"

    def set_prompt(self, prompt_text):
        """Встановлює роль і ОЧИЩАЄ стару історію"""
        self.message_list = [{"role": "system", "content": str(prompt_text)}]

    def add_message(self, content):
        """Додає повідомлення користувача"""
        self.message_list.append({"role": "user", "content": str(content)})


gpt_service = ChatGptService(token=OPENAI_API_KEY)
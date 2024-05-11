import logging
from telegram.ext import CommandHandler, MessageHandler, ApplicationBuilder, filters
from openai import OpenAI
import settings

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG)

client = OpenAI(api_key=settings.api_key)


async def start(update, context):
    context.chat_data.clear()
    await update.message.reply_text('Hi! I am your AI bot. Ask me anything!')


async def handle_message(update, context):
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='typing')
    message = update.message.text
    messages = context.chat_data.get('messages', [])
    messages.append({"role": "user", "content": message})
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{
            "role": "system",
            "content": "You are a helpful assistant."}, ] + messages
    )

    bot_response = response.choices[0].message.content
    messages.append({"role": "assistant", "content": bot_response})
    context.chat_data['messages'] = messages

    tokens = response.usage.total_tokens 
    logging.debug(f"current response tokens: {tokens}")

    if 'total_tokens' not in context.chat_data:
        context.chat_data['total_tokens'] = tokens
    else:
        context.chat_data['total_tokens'] += tokens

    await update.message.reply_text(bot_response)


async def stats(update, context):
    messages = context.chat_data.get('messages', [])
    tokens = context.chat_data.get('total_tokens', 0)
    text = f"messages: {len(messages)}\ntokens: {tokens}"
    await update.message.reply_text(text)


def main():
    application = ApplicationBuilder().token(settings.telegram_bot_token).build()

    application.add_handler(CommandHandler(["start", "help"], start))
    application.add_handler(CommandHandler(["stats",], stats))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND,
                                           handle_message))
    application.run_polling()


if __name__ == '__main__':
    main()

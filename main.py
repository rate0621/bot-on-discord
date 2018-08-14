import discord
import re,os

import Actions

client = discord.Client()

BOT_TOKEN  = os.getenv("DISCORD_BOT_TOKEN", "")

@client.event
async def on_ready():
  print('Logged in as')
  print(client.user.name)
  print(client.user.id)
  print('------')

@client.event
async def on_message(message):
  # 送り主がBotだった場合はスルー
  if client.user != message.author:
    act = Actions.Actions()
    res_type, res = act.check_and_response(message)

#    for i in client.get_all_emojis():
#      print (i)

    if res_type == 'file':
      await client.send_file(message.channel, res)
    if res_type == 'text':
      await client.send_message(message.channel, res)
    if res_type == 'emoji':
      for e in res:
        await client.add_reaction(message, e)


client.run(BOT_TOKEN)

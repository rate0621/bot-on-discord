import discord
import re,os
import setproctitle
import emoji
import configparser

import Actions
import ManageActions

import common_lib.PriDb as PriDb


client = discord.Client()
config = configparser.ConfigParser()
config.read('./secret/config.ini')

BOT_TOKEN           = os.getenv("DISCORD_BOT_TOKEN", "")
OWNER               = int(os.getenv("DISCO_SERVER_OWNER", ""))
FIRST_LOOK_CHANNEL  = int(os.getenv("FIRST_LOOK_CHANNEL_ID", ""))
FIRST_LOOK_MESSAGE  = int(os.getenv("FIRST_LOOK_MESSAGE_ID", ""))
OREKISHI_ROLE_ID    = int(os.getenv("OREKISHI_ROLE_ID", ""))
OREKISHI_ROLE_EMOJI = int(os.getenv("OREKISHI_ROLE_EMOJI_ID", ""))
TOWA_ROLE_ID        = int(os.getenv("TOWA_ROLE_ID", ""))
TOWA_ROLE_EMOJI     = int(os.getenv("TOWA_ROLE_EMOJI_ID", ""))

def remove_emoji(src_str):
    return ''.join(c for c in src_str if c not in emoji.UNICODE_EMOJI)


@client.event
async def on_member_join(member):
    for section in config.sections():
        if str(member.guild.id) == config[section]['server_id']:

            channel = discord.utils.get(member.guild.channels, name='雑談総合', type=discord.ChannelType.text)

            if channel is not None:
                here = os.path.join(os.path.dirname(os.path.abspath(__file__)))
                filepath = here + '/static/priconne/invite.jpg'
                file_image = discord.File(filepath)
                await channel.send(file=file_image, content='みなさーん！新しい仲間が来ましたよー！！')

                if section == 'OREKISHI':
                #if section == 'RATE-DEV':

                    look_channel = client.get_channel(FIRST_LOOK_CHANNEL)
                    user = client.get_user(OWNER)

                    await channel.send("まずはこちらの板のほうを確認お願いしてくださいね！\n" + look_channel.mention + "\n もしクランや鯖についてなにかわからないことがあったら。\n" + client.get_user(OWNER).mention + "に連絡してください。")

                    #role = discord.utils.get(member.guild.roles, name='騎士くん')
                    role = member.guild.get_role(OREKISHI_ROLE_ID)
                    if role is not None:
                        await member.add_roles(role)



@client.event
async def on_raw_reaction_add(payload):
    if payload.message_id == FIRST_LOOK_MESSAGE:
        checked_emoji = payload.emoji.id

        guild_id = payload.guild_id
        guild = discord.utils.find(lambda g: g.id == guild_id, client.guilds)
        if checked_emoji == OREKISHI_ROLE_EMOJI:
            role = guild.get_role(OREKISHI_ROLE_ID)
            await payload.member.add_roles(role)
        elif checked_emoji == TOWA_ROLE_EMOJI:
            role = guild.get_role(TOWA_ROLE_ID)
            await payload.member.add_roles(role)


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


@client.event
async def on_message(message):

    # botへのメンションのときの動作(主に管理者用)
    if str(client.user.id) in message.content:
        mact = ManageActions.ManageActions()
        mact.check_and_action(message)

    else:
        # 送り主がBotだった場合はスルー
        if client.user != message.author:

#            # 発言の内容をDBに格納
#            
#            text = remove_emoji(message.content)
#
#            if text != '':
#                pridb = PriDb.PriDb()
#                pridb.insert_talk(
#                    message.server.id,
#                    message.author.id,
#                    text,
#                    message.timestamp.strftime("%Y/%m/%d %H:%M:%S")
#                )
#
#
            act = Actions.Actions()
            res_type, res = act.check_and_response(message)

    #    for i in client.get_all_emojis():
    #      print (i)

            if res_type == 'file':
                file_image = discord.File(res)
                await message.channel.send(file=file_image)
            if res_type == 'text':
                await message.channel.send(res)
#            if res_type == 'emoji':
#                for e in res:
#                    await client.add_reaction(message, e)



# プロセス名設定
name, ext = os.path.splitext(os.path.basename(__file__))
setproctitle.setproctitle(os.path.basename(name))

client.run(BOT_TOKEN)

# -*- coding: utf-8 -*-

import os
import re
import discord

TOKEN = os.environ['DISCORD_BOT_TOKEN']
recruitment_message_id = 0

# 接続に必要なオブジェクトを生成
client = discord.Client()

@client.event
async def on_ready():
    """起動時に呼ばれる"""

    # 起動したらターミナルにログイン通知が表示される
    print('ログインしました')

@client.event
async def on_message(message):
    """メッセージ受信時に呼ばれる"""

    # メッセージ送信者がBotだった場合は無視する
    if message.author.bot:
        return
    if message.content == '/一覧':
        await list_participants(message.channel)
    if message.content == '/人数':
        await appear_number(message.channel)
    if message.content.startswith('/募集'):
        match1 = re.match(r'^/募集(\D*)(?P<start_hour>[0-9]{1,2})(\D*)$', message.content)
        match2 = re.match(r'^/募集(\D*)(?P<start_hour>[0-9]{1,2})-(?P<end_hour>[0-9]{1,2})(\D*)$', message.content)
        if match1:
            start_hour = match1.group('start_hour')
            await recruitment_participants(message.channel, start_hour=start_hour)
        elif match2:
            start_hour = match2.group('start_hour')
            end_hour = match2.group('end_hour')
            await recruitment_participants(message.channel, start_hour=start_hour, end_hour=end_hour)
        else:
            await recruitment_participants(message.channel)

@client.event
async def on_raw_reaction_add(payload):
    """メッセージにリアクションがつくと呼ばれる"""

    global recruitment_message_id
    if recruitment_message_id != payload.message_id:
        # 最新の募集メッセージについたリアクションでなければ返す
        return
        
    # channel_id から Channel オブジェクトを取得
    channel = client.get_channel(payload.channel_id)
    # 最新の募集メッセージのmessageオブジェクトを取得
    message = await channel.fetch_message(recruitment_message_id)

    user_list = []
    # メッセージについているリアクションを取得
    for reaction in message.reactions:
        # リアクションをつけたユーザー名を取得
        reaction_users = await reaction.users().flatten()
        for reaction_user in reaction_users:
            reaction_user_name, _ = str(reaction_user).split('#')
            user_list.append(reaction_user_name)

    # 重複削除
    user_list = list(set(user_list))
            
    min_persons = 6 - len(user_list)
    max_persons = 8 - len(user_list)
    await channel.send('現在の参加者は%s人です\n@%s-%s' % (str(len(user_list)), min_persons, max_persons))

async def list_participants(channel):
    """現在の参加者の一覧を表示"""

    # 最新の募集メッセージのmessageオブジェクトを取得
    global recruitment_message_id
    message = await channel.fetch_message(recruitment_message_id)

    user_list = []
    # メッセージについているリアクションを取得
    for reaction in message.reactions:
        # リアクションをつけたユーザー名を取得
        reaction_users = await reaction.users().flatten()
        for reaction_user in reaction_users:
            reaction_user_name, _ = str(reaction_user).split('#')
            user_list.append(reaction_user_name)

    # 重複削除
    user_list = list(set(user_list))

    if not user_list:
        await channel.send('現在の参加者は0人です')
        return

    await channel.send('現在の参加者は%s人です' % str(len(user_list)))
    for user in user_list:
        await channel.send(user)

async def appear_number(channel):
    """現在の参加人数を表示する"""

    global recruitment_message_id
        
    # 最新の募集メッセージのmessageオブジェクトを取得
    message = await channel.fetch_message(recruitment_message_id)

    user_list = []
    # メッセージについているリアクションを取得
    for reaction in message.reactions:
        # リアクションをつけたユーザー名を取得
        reaction_users = await reaction.users().flatten()
        for reaction_user in reaction_users:
            reaction_user_name, _ = str(reaction_user).split('#')
            user_list.append(reaction_user_name)

    # 重複削除
    user_list = list(set(user_list))
            
    min_persons = 6 - len(user_list)
    max_persons = 8 - len(user_list)
    await channel.send('現在の参加者は%s人です\n@%s-%s' % (str(len(user_list)), min_persons, max_persons))

async def recruitment_participants(channel, start_hour=None, end_hour=None):
    """募集をかける"""
    if (not start_hour) and (not end_hour):
        await channel.send('@here\nProjectWinter対戦募集します\n6人～8人集まれば開催します')
    elif start_hour and (not end_hour):
        await channel.send('@here\nProjectWinter対戦募集します\n%s時頃に6人～8人集まれば開催します' % start_hour)
    else:
        await channel.send('@here\nProjectWinter対戦募集します\n%s時～%s時頃に6人～8人集まれば開催します' % (start_hour, end_hour))

    # 募集メッセージのIDを記録
    # このメッセージについたリアクションで参加者を判断する
    global recruitment_message_id
    recruitment_message_id = channel.last_message_id

# Botの起動とDiscordサーバーへの接続
client.run(TOKEN)

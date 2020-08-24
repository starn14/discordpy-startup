# -*- coding: utf-8 -*-

import os
import re
import random

import discord

TOKEN = os.environ['DISCORD_BOT_TOKEN']

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
        return
    if message.content == '/人数':
        await appear_number(message.channel)
        return
    if message.content.startswith('/募集'):
        match1 = re.match(r'^/募集(\D*)(?P<start_hour>[0-9]{1,2})(\D*)$', message.content)
        match2 = re.match(r'^/募集(\D*)(?P<start_hour>[0-9]{1,2})-(?P<end_hour>[0-9]{1,2})(\D*)$', message.content)
        if match1:
            start_hour = match1.group('start_hour')
            await recruitment_participants(message, start_hour=start_hour)
        elif match2:
            start_hour = match2.group('start_hour')
            end_hour = match2.group('end_hour')
            await recruitment_participants(message, start_hour=start_hour, end_hour=end_hour)
        else:
            await recruitment_participants(message)
        return
    if client.user in message.mentions:
        await reply(message.channel, message.author)
        return

async def reply(channel, author):
    """@で話しかけられた時の応答"""
    rand = random.randrange(10)
    if rand == 0:
        msg = u'うるせえ話しかけんな（情緒不安定）'
    elif rand == 1:
        msg = u'こんにちは'
    elif rand == 2:
        msg = u'雪山人集まるかなぁ...'
    elif rand == 3:
        msg = u'ホットパイが食べたくなってきました'
    elif rand == 4:
        msg = u'近接武器はやっぱり鎌ですよね'
    elif rand == 5:
        msg = u'近接武器はやっぱりピッケルですよね'
    elif rand == 6:
        msg = u'近接武器はやっぱり斧ですよね'
    elif rand == 7:
        msg = u'今日の通信機のラッキーカラーは黄色！'
    elif rand == 8:
        msg = u'今日の通信機のラッキーカラーは青色！'
    elif rand == 9:
        msg = u'今日の通信機のラッキーカラーは赤色！ シーッ！'

    reply = f'{author.mention} %s' % msg
    await channel.send(reply)

@client.event
async def on_raw_reaction_add(payload):
    """メッセージにリアクションがつくと呼ばれる"""
        
    # channel_id から Channel オブジェクトを取得
    channel = client.get_channel(payload.channel_id)

    # 過去のメッセージを遡って募集メッセージを探す
    message = await get_last_recruitment_message(channel)
    if payload.message_id != message.id:
        # 募集メッセージについたリアクションでなければ返す
        return
        
    # リアクションのついた募集メッセージのmessageオブジェクトを取得
    message = await channel.fetch_message(payload.message_id)

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
            
    if len(user_list) <= 5:
        min_persons = 6 - len(user_list)
        max_persons = 8 - len(user_list)
        await channel.send('現在の参加者は%s人です\n@%s-%s' % (str(len(user_list)), min_persons, max_persons))
    elif len(user_list) >= 6 and len(user_list) <= 7:
        max_persons = 8 - len(user_list)
        await channel.send('現在の参加者は%s人です\nゲーム開始できます! なお、@%s人まで参加可能です' % (str(len(user_list)), max_persons))
    elif len(user_list) == 8:
        await channel.send('現在の参加者は%s人です\n8人揃ってます!' % (str(len(user_list))))
    elif len(user_list) >= 9:
        amari_persons = 9 - len(user_list)
        await channel.send('現在の参加者は%s人です\n申し訳ありませんが、%s人観戦となります' % (str(len(user_list)), amari_persons))

async def list_participants(channel):
    """現在の参加者の一覧を表示"""

    # 過去のメッセージを遡って募集メッセージを探す
    message = await get_last_recruitment_message(channel)

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

    msg = '現在の参加者は%s人です\n' % str(len(user_list))
    msg += '\n'.join(user_list)
    await channel.send(msg)

async def appear_number(channel):
    """現在の参加人数を表示する"""

    # 過去のメッセージを遡って募集メッセージを探す
    message = await get_last_recruitment_message(channel)

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

async def recruitment_participants(message, start_hour=None, end_hour=None):
    """募集をかける"""
    if (not start_hour) and (not end_hour):
        await message.channel.send('@here\nProjectWinter対戦募集します\n6人～8人集まれば開催します\n参加する方はこのメッセージにリアクションをつけてください')
    elif start_hour and (not end_hour):
        await message.channel.send('@here\nProjectWinter対戦募集します\n%s時頃に6人～8人集まれば開催します\n参加する方はこのメッセージにリアクションをつけてください' % start_hour)
    else:
        await message.channel.send('@here\nProjectWinter対戦募集します\n%s時～%s時頃に6人～8人集まれば開催します\n参加する方はこのメッセージにリアクションをつけてください' % (start_hour, end_hour))

async def get_last_recruitment_message(channel):
    async for message in channel.history(limit=500):
        if not message.author.bot:
            continue
        if message.content.startswith('@here\nProjectWinter対戦募集します'):
            return message

# Botの起動とDiscordサーバーへの接続
client.run(TOKEN)

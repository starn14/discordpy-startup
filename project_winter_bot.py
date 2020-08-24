# -*- coding: utf-8 -*-

import os
import re
import random

import discord

TOKEN = os.environ['DISCORD_BOT_TOKEN']
os.environ['PW_BOT_MSG_ID'] = 0

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
            await recruitment_participants(message.channel, start_hour=start_hour)
        elif match2:
            start_hour = match2.group('start_hour')
            end_hour = match2.group('end_hour')
            await recruitment_participants(message.channel, start_hour=start_hour, end_hour=end_hour)
        else:
            await recruitment_participants(message.channel)
        return
    if message.content.startswith('@雪山bot'):
        await reply(message.channel)
        return

async def reply(channel):
    """@で話しかけられた時の応答"""
    rand = random.randrange(10)
    if rand == 0:
        await channel.send(u'うるせえ話しかけんな（情緒不安定）')
    elif rand == 1:
        await channel.send(u'こんにちは')
    elif rand == 2:
        await channel.send(u'雪山人集まるかなぁ...')
    elif rand == 3:
        await channel.send(u'ホットパイが食べたくなってきました')
    elif rand == 4:
        await channel.send(u'近接武器はやっぱり鎌ですよね')
    elif rand == 5:
        await channel.send(u'近接武器はやっぱりピッケルですよね')
    elif rand == 6:
        await channel.send(u'近接武器はやっぱり斧ですよね')
    elif rand == 7:
        await channel.send(u'今日の通信機のラッキーカラーは黄色！')
    elif rand == 8:
        await channel.send(u'今日の通信機のラッキーカラーは青色！')
    elif rand == 9:
        await channel.send(u'今日の通信機のラッキーカラーは赤色！ シーッ！')

@client.event
async def on_raw_reaction_add(payload):
    """メッセージにリアクションがつくと呼ばれる"""

    if os.environ['PW_BOT_MSG_ID'] != payload.message_id:
        # 最新の募集メッセージについたリアクションでなければ返す
        return
        
    # channel_id から Channel オブジェクトを取得
    channel = client.get_channel(payload.channel_id)
    # 最新の募集メッセージのmessageオブジェクトを取得
    message = await channel.fetch_message(os.environ['PW_BOT_MSG_ID'])

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

    # 最新の募集メッセージのmessageオブジェクトを取得
    try:
        message = await channel.fetch_message(os.environ['PW_BOT_MSG_ID'])
    except discord.errors.NotFound:
        await channel.send('募集メッセージが見つかりません')
        return

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

    # 最新の募集メッセージのmessageオブジェクトを取得
    try:
        message = await channel.fetch_message(os.environ['PW_BOT_MSG_ID'])
    except discord.errors.NotFound:
        await channel.send('募集メッセージが見つかりません')
        return

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
        await channel.send('@here\nProjectWinter対戦募集します\n6人～8人集まれば開催します\n参加する方はこのメッセージにリアクションをつけてください')
    elif start_hour and (not end_hour):
        await channel.send('@here\nProjectWinter対戦募集します\n%s時頃に6人～8人集まれば開催します\n参加する方はこのメッセージにリアクションをつけてください' % start_hour)
    else:
        await channel.send('@here\nProjectWinter対戦募集します\n%s時～%s時頃に6人～8人集まれば開催します\n参加する方はこのメッセージにリアクションをつけてください' % (start_hour, end_hour))

    # 募集メッセージのIDを記録
    # このメッセージについたリアクションで参加者を判断する
    os.environ['PW_BOT_MSG_ID'] = channel.last_message_id

# Botの起動とDiscordサーバーへの接続
client.run(TOKEN)

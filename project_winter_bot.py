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
    rand = random.randrange(40)

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
    elif rand == 10:
        msg = u'えー！私人狼じゃないですよぉ！'
    elif rand == 11:
        msg = u'今日の第一修理目標の素材は...歯車%s/基盤%s/燃料%s' % (str(random.randrange(6, 16)), str(random.randrange(6, 16)), str(random.randrange(6, 16)))
    elif rand == 12:
        msg = u'今日の第一修理目標は...発掘！ さあスコップを持って！'
    elif rand == 13:
        msg = u'今日の第一修理目標は...暗号！ ...117？'
    elif rand == 14:
        msg = u'今日の第二修理目標の素材は...歯車%s/基盤%s/燃料%s' % (str(random.randrange(6, 16)), str(random.randrange(6, 16)), str(random.randrange(6, 16)))
    elif rand == 15:
        msg = u'今日の第二修理目標は...アニマルラッシュ！ シロクマに気を付けてね！'
    elif rand == 16:
        msg = u'今日の第二修理目標は...運搬！'
    elif rand == 17:
        msg = u'ブロニキ～～～～？？？？？？'
    elif rand == 18:
        msg = u'今日のBLACKOUTラッキーアイテムは...ロザリオ！'
    elif rand == 19:
        msg = u'今日のBLACKOUTラッキーアイテムは...松明！'
    elif rand == 20:
        msg = u'今日のBLACKOUTラッキーアイテムは...聖書！'
    elif rand == 21:
        msg = u'あなたをロールに例えると...イノセントかな！ 何の特徴もないんだね！'
    elif rand == 22:
        msg = u'あなたをロールに例えると...サイエンティストかな！ 頭良さそうに見えて大して役に立たない人？'
    elif rand == 23:
        msg = u'あなたをロールに例えると...ハッカーかな！ ぼっちでも安心！'
    elif rand == 24:
        msg = u'あなたをロールに例えると...ソルジャーかな！ 頼りになる～！'
    elif rand == 25:
        msg = u'あなたをロールに例えると...ディフェクターかな！ どっちつかずって感じのあなたにピッタリ！'
    elif rand == 26:
        msg = u'あなたをロールに例えると...メディックかな！ 癒し系に見えていざという時まで何もしない人？'
    elif rand == 27:
        msg = u'あなたをロールに例えると...ディテクティブかな！ かゆいところに手が届かない人ってよく言われない？'
    elif rand == 28:
        msg = u'あなたをロールに例えると...ハンターかな！ 頑固すぎて周りから浮いちゃうこと、ない？？'
    elif rand == 29:
        msg = u'あなたをロールに例えると...パードレかな！ 他力本願って楽でいいよね～'
    elif rand == 30:
        msg = u'あなたをロールに例えると...デーモンかな！ 強そうな名前だけど実は孤独な人なんだね...'
    elif rand == 31:
        msg = u'あなたをロールに例えると...ウィスパラーかな！ 周囲からは挙動不審な人だと思われてるよ！'
    elif rand == 32:
        msg = u'あなたをロールに例えると...イエティかな！ 性格悪いって言われない？'
    elif rand == 33:
        msg = u'あなたをロールに例えると...アイデンティティシーフかな！ 一つ分の陽だまりに二つはちょっと入れないんだよね'
    elif rand == 34:
        msg = u'あなたをロールに例えると...ヒマンチュかな！ ...あっすません、すません...'
    elif rand == 35:
        msg = u'今日のラッキーイベントは...ブリザード！ 引きこもる理由にはうってつけだね！'
    elif rand == 36:
        msg = u'今日のラッキーイベントは...ウサギ！ リアル狂人達の独壇場だ！'
    elif rand == 37:
        msg = u'今日のラッキーイベントは...ソーラーフレア！ ...あっ看板回しとこ...'
    elif rand == 38:
        msg = u'今日のラッキーイベントは...支援物資投下！ 取れると思った？？残念、罠でした！'
    elif rand == 39:
        msg = u'今日のラッキーイベントは...脱出ポッド！ 誰しも自分の身が一番大事！'

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
    if not message:
        await channel.send('過去の募集メッセージが見つかりません')
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

    # 過去のメッセージを遡って募集メッセージを探す
    message = await get_last_recruitment_message(channel)
    if not message:
        await channel.send('過去の募集メッセージが見つかりません')
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

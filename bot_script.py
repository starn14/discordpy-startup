# -*- coding: utf-8 -*-

import os
import re
import random
import asyncio  
from collections import namedtuple  

from discord.ext import commands
import discord

TOKEN_PW = os.environ['DISCORD_BOT_TOKEN_PW']
TOKEN_KUROMAKU = os.environ['DISCORD_BOT_TOKEN_KUROMAKU']

class ProjectWinterBot(discord.Client):

    async def on_ready(self):
        """起動時に呼ばれる"""
        # 起動したらターミナルにログイン通知が表示される
        print('ログインしました')

    async def on_message(self, message):
        """メッセージ受信時に呼ばれる"""

        # メッセージ送信者がBotだった場合は無視する
        if message.author.bot:
            return
        if message.content == '/一覧':
            await self.list_participants(message.channel)
            return
        if message.content == '/人数':
            await self.appear_number(message.channel)
            return
        if message.content.startswith('/募集'):
            match1 = re.match(r'^/募集(\D*)(?P<start_hour>[0-9]{1,2})(\D*)$', message.content)
            match2 = re.match(r'^/募集(\D*)(?P<start_hour>[0-9]{1,2})-(?P<end_hour>[0-9]{1,2})(\D*)$', message.content)
            if match1:
                start_hour = match1.group('start_hour')
                await self.recruitment_participants(message, start_hour=start_hour)
            elif match2:
                start_hour = match2.group('start_hour')
                end_hour = match2.group('end_hour')
                await self.recruitment_participants(message, start_hour=start_hour, end_hour=end_hour)
            else:
                await self.recruitment_participants(message)
            return
        if self.user in message.mentions:
            await self.reply(message.channel, message.author)
            return

    async def on_raw_reaction_add(self, payload):
        """メッセージにリアクションがつくと呼ばれる"""
            
        # channel_id から Channel オブジェクトを取得
        channel = self.get_channel(payload.channel_id)

        # 過去のメッセージを遡って募集メッセージを探す
        message = await self.get_last_recruitment_message(channel)
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

    async def reply(self, channel, author):
        """@で話しかけられた時の応答"""
        msg_list = [
            u'うるせえ話しかけんな（情緒不安定）',
            u'こんにちは',
            u'雪山人集まるかなぁ...',
            u'ホットパイが食べたくなってきました',
            u'近接武器はやっぱり鎌ですよね',
            u'近接武器はやっぱりピッケルですよね',
            u'近接武器はやっぱり斧ですよね',
            u'今日の通信機のラッキーカラーは黄色！',
            u'今日の通信機のラッキーカラーは青色！',
            u'今日の通信機のラッキーカラーは赤色！ シーッ！',
            u'えー！私人狼じゃないですよぉ！',
            u'今日の第一修理目標の素材は...歯車%s/基盤%s/燃料%s' % (str(random.randrange(6, 16)), str(random.randrange(6, 16)), str(random.randrange(6, 16))),
            u'今日の第一修理目標は...発掘！ さあスコップを持って！',
            u'今日の第一修理目標は...暗号！ ...117？',
            u'今日の第二修理目標の素材は...歯車%s/基盤%s/燃料%s' % (str(random.randrange(6, 16)), str(random.randrange(6, 16)), str(random.randrange(6, 16))),
            u'今日の第二修理目標は...アニマルラッシュ！ シロクマに気を付けてね！',
            u'今日の第二修理目標は...運搬！',
            u'ブロニキ～～～～？？？？？？',
            u'今日のBLACKOUTラッキーアイテムは...ロザリオ！',
            u'今日のBLACKOUTラッキーアイテムは...松明！',
            u'今日のBLACKOUTラッキーアイテムは...聖書！',
            u'あなたをロールに例えると...イノセントかな！\n何の特徴もないんだね！',
            u'あなたをロールに例えると...サイエンティストかな！\n頭良さそうに見えて大して役に立たない人？',
            u'あなたをロールに例えると...ハッカーかな！\nぼっちでも安心！',
            u'あなたをロールに例えると...ソルジャーかな！\n頼りになる～！',
            u'あなたをロールに例えると...ディフェクターかな！\nどっちつかずって感じのあなたにピッタリ！',
            u'あなたをロールに例えると...メディックかな！\n癒し系に見えていざという時まで何もしない人？',
            u'あなたをロールに例えると...ディテクティブかな！\nかゆいところに手が届かない人ってよく言われない？',
            u'あなたをロールに例えると...ハンターかな！\n頑固すぎて周りから浮いちゃうこと、ない？？',
            u'あなたをロールに例えると...パードレかな！\n他力本願って楽でいいよね～',
            u'あなたをロールに例えると...デーモンかな！\n強そうな名前だけど実は孤独な人なんだね...',
            u'あなたをロールに例えると...ウィスパラーかな！\n周囲からは挙動不審な人だと思われてるよ！',
            u'あなたをロールに例えると...イエティかな！\n性格悪いって言われない？',
            u'あなたをロールに例えると...アイデンティティシーフかな！\n一つ分の陽だまりに二つはちょっと入れないんだよね',
            u'あなたをロールに例えると...ヒマンチュかな！\n...あっすません、すません...',
            u'今日のラッキーイベントは...ブリザード！\n引きこもる理由にはうってつけだね！',
            u'今日のラッキーイベントは...ウサギ！\nリアル狂人達の独壇場だ！',
            u'今日のラッキーイベントは...ソーラーフレア！\n...あっ看板回しとこ...',
            u'今日のラッキーイベントは...支援物資投下！取れると思った？？残念、罠でした！',
            u'今日のラッキーイベントは...脱出ポッド！ 誰しも自分の身が一番大事！',
            u'[雪山豆知識] 鎌で最も射程の長い武器は、ハロウィンシックルです！\nハロウィン限定装備です',
            u'[雪山豆知識] ピッケルで最も射程の長い武器は、オークスティールハンマーです！\nリワードで手に入ります！',
            u'[雪山豆知識] 斧で最も射程の長い武器は、金の斧です！\n4000円箱で手に入ります！',
            u'[雪山豆知識] トレイターチェストは、トレイターかディフェクターしか開けられません\n中にアイテムを保管する使い方もあります',
            u'[雪山豆知識] 近接武器は、100%チャージしてしまうと、\n攻撃後の後隙が大きくなってしまいます',
            u'[雪山豆知識] 近接武器は、攻撃の判定がしばらく残るので、\n回転しながら殴った方が広範囲を攻撃できます',
            u'[雪山豆知識] 近接武器で戦う場合は、\n連打ではなく溜めてから攻撃した方がDPSが高いです！',
            u'[雪山豆知識] ベリーは採取後しばらくすると復活します',
            u'[雪山豆知識] 薬草は鎌の溜め攻撃なら一撃で破壊することができます',
            u'[雪山豆知識] カメラの関係で、遠距離戦では下側を陣取っている方が視界が広く有利です',
            u'[雪山豆知識] 遠距離武器のコツは、レティクルの収束をしっかり待ってから、\n敵にカーソルを合わせて撃つことです',
            u'[雪山豆知識] 狼相手の戦いは、敵の攻撃を真横に回避しながら攻撃するのが良いです',
            u'[雪山豆知識] マップは全部で6種類あります 建物の位置などは毎回変動します',
            u'[雪山豆知識] 狼マップ（マップに山を越える三本の橋がある）では、\nNW / NE / S にトレイターチェストが出現しません',
            u'[雪山豆知識] トレイターチェストは、ひとつのエリアに4つまでしか出現しません\n4つ開けたら次に行きましょう',
            u'[雪山豆知識] トレイターは黄色/青色の通信機を持つと、赤色通信機が使えなくなってしまいます\nただし、通常のインベントリに入れれば、会話を聞くことだけはできます',
            u'[雪山豆知識] アイテムクラフト後にインベントリに空きがないと、\n作ったアイテムを足元に落としてしまいます',
            u'[雪山豆知識] トレイターのドリンクは 黒 > 赤 > 青 の順に上昇量が高いです',
            u'[雪山豆知識] 興奮剤は、移動力だけでなく攻撃力もあがります',
            u'[雪山豆知識] 発掘ミッションでは、発掘するアイテムに近づくと\n「ゴウンゴウン」という音が聞こえます',
            u'[雪山豆知識] 焚火には木か燃料を追加して燃焼時間を増やすことができます\n燃料の場合は、追加後一定時間すると爆発するので注意！',
        ]
        rand = random.randrange(len(msg_list))
        msg = msg_list[rand]

        reply = f'{author.mention}\n%s' % msg
        await channel.send(reply)

    async def list_participants(self, channel):
        """現在の参加者の一覧を表示"""

        # 過去のメッセージを遡って募集メッセージを探す
        message = await self.get_last_recruitment_message(channel)
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

    async def appear_number(self, channel):
        """現在の参加人数を表示する"""

        # 過去のメッセージを遡って募集メッセージを探す
        message = await self.get_last_recruitment_message(channel)
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

    async def recruitment_participants(self, message, start_hour=None, end_hour=None):
        """募集をかける"""
        if (not start_hour) and (not end_hour):
            await message.channel.send('@here\nProjectWinter対戦募集します\n6人～8人集まれば開催します\n参加する方はこのメッセージにリアクションをつけてください')
        elif start_hour and (not end_hour):
            await message.channel.send('@here\nProjectWinter対戦募集します\n%s時頃に6人～8人集まれば開催します\n参加する方はこのメッセージにリアクションをつけてください' % start_hour)
        else:
            await message.channel.send('@here\nProjectWinter対戦募集します\n%s時～%s時頃に6人～8人集まれば開催します\n参加する方はこのメッセージにリアクションをつけてください' % (start_hour, end_hour))

    async def get_last_recruitment_message(self, channel):
        async for message in channel.history(limit=500):
            if not message.author.bot:
                continue
            if message.content.startswith('@here\nProjectWinter対戦募集します'):
                return message

class KuromakuBot(discord.Client):

    async def on_ready(self):
        """起動時に呼ばれる"""
        # 起動したらターミナルにログイン通知が表示される
        print('くろまくログインしました')

    async def on_message(self, message):
        # メッセージ送信者がBotだった場合は無視する
        if message.author.bot:
            return
        if message.content == 'hoge':
            await message.channel.send('huga')


Entry = namedtuple('Entry', 'client event token')  
entries = [  
    Entry(client=ProjectWinterBot(), event=asyncio.Event(), token=TOKEN_PW),  
    Entry(client=KuromakuBot(), event=asyncio.Event(), token=TOKEN_KUROMAKU)  
]  

async def login():  
    for e in entries:  
        await e.client.login(e.token)  

async def wrapped_connect(entry):  
    try:  
        await entry.client.connect()  
    except Exception as e:  
        await entry.client.close()  
        print('We got an exception: ', e.__class__.__name__, e)  
        entry.event.set()  

async def check_close():  
    futures = [e.event.wait() for e in entries]  
    await asyncio.wait(futures)  

loop = asyncio.get_event_loop()  
loop.run_until_complete(login())  
for entry in entries:  
    loop.create_task(wrapped_connect(entry))  
loop.run_until_complete(check_close())  
loop.close()

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
        print(u'雪山Bot、参上！')

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
            u'[雪山豆知識]\n鎌で最も射程の長い武器は、ハロウィンシックルです！\nハロウィン限定装備です',
            u'[雪山豆知識]\nピッケルで最も射程の長い武器は、オークスティールハンマーです！\nリワードで手に入ります！',
            u'[雪山豆知識]\n斧で最も射程の長い武器は、金の斧です！\n4000円箱で手に入ります！',
            u'[雪山豆知識]\nトレイターチェストは、トレイターかディフェクターしか開けられません\n中にアイテムを保管する使い方もあります',
            u'[雪山豆知識]\n近接武器は、100%チャージしてしまうと、\n攻撃後の後隙が大きくなってしまいます',
            u'[雪山豆知識]\n近接武器は、攻撃の判定がしばらく残るので、\n回転しながら殴った方が広範囲を攻撃できます',
            u'[雪山豆知識]\n近接武器で戦う場合は、\n連打ではなく溜めてから攻撃した方がDPSが高いです！',
            u'[雪山豆知識]\nベリーは採取後2分30秒すると復活します',
            u'[雪山豆知識]\n薬草は鎌の溜め攻撃なら一撃で破壊することができます',
            u'[雪山豆知識]\nカメラの関係で、遠距離戦では下側を陣取っている方が視界が広く有利です',
            u'[雪山豆知識]\n遠距離武器のコツは、レティクルの収束をしっかり待ってから、\n敵にカーソルを合わせて撃つことです',
            u'[雪山豆知識]\n狼相手の戦いは、敵の攻撃を真横に回避しながら攻撃するのが良いです',
            u'[雪山豆知識]\nマップは全部で6種類あります 建物の位置などは毎回変動します',
            u'[雪山豆知識]\n狼マップ（マップに山を越える三本の橋がある）では、\nNW / NE / S にトレイターチェストが出現しません',
            u'[雪山豆知識]\nトレイターチェストは、ひとつのエリアに4つまでしか出現しません\n4つ開けたら次に行きましょう',
            u'[雪山豆知識]\nトレイターは黄色/青色の通信機を持つと、赤色通信機が使えなくなってしまいます\nただし、通常のインベントリに入れれば、会話を聞くことだけはできます',
            u'[雪山豆知識]\nアイテムクラフト後にインベントリに空きがないと、\n作ったアイテムを足元に落としてしまいます',
            u'[雪山豆知識]\nトレイターのドリンクは 黒 > 赤 > 青 の順に上昇量が高いです',
            u'[雪山豆知識]\n興奮剤は、移動力だけでなく攻撃力もあがります',
            u'[雪山豆知識]\n発掘ミッションでは、発掘するアイテムに近づくと\n「ゴウンゴウン」という音が聞こえます',
            u'[雪山豆知識]\n焚火には木か燃料を追加して燃焼時間を増やすことができます\n燃料の場合は、追加後一定時間すると爆発するので注意！',
            u'[雪山豆知識]\n空きインベントリを選択していると、移動速度がわずかに上がります',
            u'[雪山豆知識]\n上り坂では、移動速度が下がります',
            u'[雪山豆知識]\nアイテムの出し入れの際は、ドラッグよりも右クリックの方が楽です\nスタックしたアイテムを一括移動させる場合は、Shift + 左クリックです',
            u'[雪山豆知識]\n空腹は1秒で1減少します',
            u'[雪山豆知識]\n体温は1秒で2減少します',
            u'[雪山豆知識]\n応急処置キットは毒状態も回復させることができます',
            u'[雪山豆知識]\n焚火の効果は重複します',
            u'[雪山豆知識]\nバックパックは1つしか作成できません',
            u'[雪山豆知識]\n近接武器は投擲で当てることで、フルチャージと同程度のダメージを与えます',
            u'[雪山豆知識]\n罠解除キット（電子基板）は、地雷を解除することができますが、\n解除した地雷はその場で爆発します',
            u'[雪山豆知識]\n罠解除キット（電子基板）は、毒を解除することはできません',
            u'[雪山豆知識]\nS方向は視野が狭く、また、声も届きにくいです',
            u'[雪山豆知識]\n近接武器の溜め攻撃はチャージが70%以上で放つと、\n相手にスローをかけることができます',
            u'[雪山豆知識]\nトレイター専用の赤色の通信機は、\n持ち主が死亡するとインベントリから消滅します',
            u'[雪山豆知識]\nドリンクによる各ステータスのバフは、\n最初のHPを基準に計算します',
            u'[雪山豆知識]\nダウンしても、ダメージを受けなければ1分間は生存することができます',
            u'[雪山豆知識]\n変装をした人物を追放するには、\nその変装先の人の名前を選ぶ必要があります\nただし、追放してから変装をした人物については、追放先を変える必要はありません',
            u'[雪山豆知識]\nサバイバー支援物資は、サバイバーの残りが2名以下になっている状態で、\n残り分数が5の倍数になると投下されます',
            u'[雪山豆知識]\nBLACK OUTのたいまつは、体温の減少量を抑えます(1秒に0.5回復)',
            u'[雪山豆知識]\nBLACK OUTの聖書は、魔女の時間イベント中、動物に3倍のダメージを与えます',
            u'[雪山豆知識]\nデーモンはコンバートを成功させるたびに、\nゲージのチャージ時間が短くなります',
            u'[雪山豆知識]\nウィスパラーは効果の対象となる相手が少ないほど、\n相手のゲージ上昇量が増えます',
            u'[雪山豆知識]\n暗闇イベント中は、デーモンとウィスパラーのチャージ速度が上がります',
            u'[雪山豆知識]\n暗闇イベント中は、デーモンとウィスパラーのチャージ速度が上がります',
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
        print('（╭☞•́ټ•̀）╭☞՞ټ՞）')

    async def on_message(self, message):
        # メッセージ送信者がBotだった場合は無視する
        if message.author.bot:
            return
        if self.user in message.mentions:
            await self.reply(message.channel, message.author)
            return

    async def reply(self, channel, author):
        """@で話しかけられた時の応答"""

        rank_value = random.randrange(100)
        if rank_value <= 59:
            # 0 - 59 (60%)
            rank = 'Common'
            star = '★★★☆☆☆'
        elif rank_value <= 89:
            # 60 - 89 (30%)
            rank = 'Rare'
            star = '★★★★☆☆'
        elif rank_value <= 96:
            # 90 - 96 (7%)
            rank = 'SR'
            star = '★★★★★☆'
        elif rank_value <= 99:
            # 97 - 99 (3%)
            rank = 'SSR'
            star = '★★★★★★'

        msg_rank_dict = {
            'Common': {
                u'カラータイル': u'やるやん\n明日またリベンジさせて',
                u'グラブル': u'あるつよどうですか',
                u'にゃんこ大戦争': u'( ^.ټ.^)',
                u'魔女と百騎兵': u'恐ろしい風貌の最強の魔神 『くろまく』',
                u'ルフランの地下迷宮と魔女ノ旅団': u'ルカさんルカさん...',
                u'ディスガイア': u'史上最凶やり込みシミュレーションRPG\nVS\n史上最狂やり込みプレイヤーくろまく',
                u'出勤': u'折れた心',
                u'プリコネ': u'もう一人のくろまく くろまくまろく',
                u'Twitter': u'主にリツイートメイン',
                u'お絵描き': u'プロ絵師待ったなし',
                u'幻想戦略譚': u'楽勝すぎて飽きちゃった',
                u'Toppa': u'https://www.tp1.jp/',
                u'DBD': u'かかってこいキラー共',
                u'アイギス': u'R18版はまたいつかね',
                u'ポケモン': u'くろまくさんは存在が6V',
                u'TFT': u'4ヴァンガード4ミスティック1アイキン',
                u'遊戯王': u'三幻神を片手でねじ伏せた男',
                u'アイワナ': u'I wanna be the Kuromaku.',
                u'Dさん配信閲覧': u'だからくろまくさんがいたのかぁ',
                u'株': u'くろまく配信の株買わせてください',
                u'アナザーエデン': u'時空を超えるくろまく',
                u'FGO': u'聖杯に託す願いは「回線高速化」',
                u'Undertale': u'▼ たたかわず　にげもせず\nくろまくとの　バトルを　さけるには・・・？',
                u'CaveTube': u'ニコ生は糞',
                u'Ark': u'ティラノサウルスに裸片手剣で挑んだ男',
                u'残業': u'お体ご自愛下さい',
                u'本田とじゃんけん': u'ほな、いただかれます',
                u'PayDay2': u'銀行こわれる',
                u'7days to die': u'ちなみにくろまく配信が7日間無かったら私たちは生き延びられません',
                u'チルノ見参': u'「酒宴と間違えて買いました」',
                u'ペーパーマン': u'アバターはイカ娘',
                u'アークナイツ': u'酒宴で鍛えたタワーディフェンス',
                u'暇つぶし': u'暇を持て余した神々の遊び',
                u'モンハン': u'配信竜 リオクロマク',
                u'地球防衛軍': u'この戦いが終わったら...ループに戻るお(՞ټ՞)',
                u'FTL': u'スペースループ',
                u'VestariaSaga': u'ロードクロマク☆',
                u'メタルギア': u'！！！！！！！！！！！！！！！(՞ټ՞)！！！！！！！！！！！！！！！',
                u'ファイアーエムブレム': u'マイユニットはハゲ',
                u'バイオハザード': u'ゾンビ VS 徹夜配信でゾンビ化したくろまく',
                u'Trine': u'英語ストーリーで寝落ち不可避',
                u'東方心綺楼': u'116.67.228.244:10800',
                u'さとりの情操教育': u'教育されるくろまく',
                u'AOE': u'戦争とは愚か者のすることです',
                u'東方ちぇむぶれむ': u'アーマーナイトと化した星',
                u'非想天則': u'記念すべき第二回放送',
                u'Discord': u'まっこい3太郎',
            },
            'Rare': {
                u'古戦場': u'朝活(深夜1時スタート)',
                u'15永琳': u'初心者さんに対する行為が尋常じゃなく酷い',
                u'酒宴ロビー募集': u'いつもありがとうございました',
                u'コミケ参加': u'写真撮影はNGです',
                u'水がめループ': u'大きなパンを1つもってやりなおしますか？',
                u'ニコ生配信': u'生 き が い',
                u'JGグレイブス': u'Ctrl+2を連打しながらインベードして\n赤バフと敵JGを殺してBotでダブルキルを取る男',
                u'水爆祝': u'乱数調整（試行回数1000回）',
                u'開幕メガンテ変化の石像': u'トルネコ3ディスク割りました\n残り1枚です',
                u'ペンコン': u'「ポポロ異世界で一番つまらない」',
                u'諭吉投入': u'残り何枚ですか？',
                u'あしらむさんとDuoBot': u'アイキンマンとはもうやらない',
                u'地雷探知犬': u'踏んで除去するスタイル',
                u'孵化厳選': u'良いお父さんになりそう',
                u'親R': u'く～ろ～ま～く～ が切断されました',
                u'沼の魔女': u'グラブルは×××ゲー 開発者が××××で××××××××××。',
                u'年越し': u'除夜の鐘 くろまく配信 初日の出',
                u'アイキンと': u'アイキンって誰？どちらさん？\nもしかして：くろまく',
                u'春よ来い': u'お気に入りBGM',
                u'ハッシュずれ': u'原因：PCのスペックが高すぎた',
                u'Neetpiaリツイート': u'酒宴2は2050年頃',
                u'需要の無い放送局': u'需要しかありません',
                u'Steamセール': u'「飽きた」',
                u'銀の': u'5つ集めるとマイクが実装されたりされなかったり',
            },
            'SR': {
                u'東方妖々夢': u'「くろまく～」「黒幕、弱いなぁ」',
                u'キラーマシン勧誘': u'あしらむ あしらつー あしらさん\nあしらふぉ あしらごー あしっくす',
                u'スモコン': u'22の経験値を得た\n22の経験値を得た\n22の経験値を得た',
                u'寝落ち': u'アイキンまた寝落ちかよ',
                u'ホイミ': u'害悪糞青ハゲクラゲ',
                u'金の': u'ハガキに貼って応募しても何も起こりません',
            },
            'SSR': {
                u'タムケンチ無双': u'HP10%からのBotレーンDOUBLE KILL!\nちなみにADCはタワーダイブで死んだ',
                u'異世界打開': u'くろまくは 異世界の迷宮を\n無事に突破した',
                u'酒宴3000戦': u'酒宴で人生棒に振ったお',
                u'マイクあり': u'過去3回の奇跡',
            }
        }

        msg_dict = msg_rank_dict[rank]

        rand = random.randrange(len(msg_dict.keys()))
        msg_title = list(msg_dict.keys())[rand]
        msg = msg_dict[msg_title]

        reply = '\n[%s] %sくろまく\n%s\n%s' % (rank, msg_title, star, msg)

        gomi_value = random.randrange(100)
        is_gomi = (gomi_value >= 95)
        if rank == 'Common':
            await self.call_common_msg(author.mention, channel, reply, is_gomi)
        elif rank == 'Rare':
            await self.call_rare_msg(author.mention, channel, reply, is_gomi)
        elif rank == 'SR':
            await self.call_sr_msg(author.mention, channel, reply, is_gomi)
        elif rank == 'SSR':
            await self.call_ssr_msg(author.mention, channel, reply, is_gomi)
    
    async def call_gomi_msg(self, mention_author, channel, message):
        frame_str = await self._get_frame_str('Gomi')
        msg = '%s\n%s%s\n%s' % (mention_author, frame_str, u'\n----------------------------------------------------', frame_str)
        await message.edit(content=msg)

        await asyncio.sleep(1)

        reply = '\n[%s] %s\n%s\n%s' % ('Gomi', 'ごみりん', '★☆☆☆☆☆', '残念！ごみりんが出ちゃった！')
        new_msg = '%s\n%s%s\n%s' % (mention_author, frame_str, reply, frame_str)
        await message.edit(content=new_msg)

    async def call_common_msg(self, mention_author, channel, reply, is_gomi):
        frame_str_c = await self._get_frame_str('Common')
        msg = '%s\n%s%s\n%s' % (mention_author, frame_str_c, u'\n----------------------------------------------------', frame_str_c)
        message = await channel.send(msg)

        await asyncio.sleep(1)

        if not is_gomi:
            new_msg = '%s\n%s%s\n%s' % (mention_author, frame_str_c, reply, frame_str_c)
            await message.edit(content=new_msg)
        else:
            await self.call_gomi_msg(mention_author, channel, message)

    async def call_rare_msg(self, mention_author, channel, reply, is_gomi):
        frame_str_r = await self._get_frame_str('Rare')
        msg = '%s\n%s%s\n%s' % (mention_author, frame_str_r, u'\n----------------------------------------------------', frame_str_r)
        message = await channel.send(msg)

        await asyncio.sleep(1)

        if not is_gomi:
            new_msg = '%s\n%s%s\n%s' % (mention_author, frame_str_r, reply, frame_str_r)
            await message.edit(content=new_msg)
        else:
            await self.call_gomi_msg(mention_author, channel, message)

    async def call_sr_msg(self, mention_author, channel, reply, is_gomi):
        production_value = random.randrange(100)
        if production_value >= 50:
            # 確定演出
            frame_str_r = await self._get_frame_str('Rare')
            frame_str_1 = await self._get_frame_str('SR1')
            frame_str_2 = await self._get_frame_str('SR2')
            frame_str_3 = await self._get_frame_str('SR3')
            msg = '%s\n%s%s\n%s' % (mention_author, frame_str_r, u'\n----------------------------------------------------', frame_str_r)
            message = await channel.send(msg)

            await asyncio.sleep(1)

            new_msg = '%s\n%s%s\n%s' % (mention_author, frame_str_1, u'\n----------------------------------------------------', frame_str_1)
            await message.edit(content=new_msg)

            await asyncio.sleep(0.25)

            new_msg = '%s\n%s%s\n%s' % (mention_author, frame_str_2, u'\n----------------------------------------------------', frame_str_2)
            await message.edit(content=new_msg)

            await asyncio.sleep(0.25)

            new_msg = '%s\n%s%s\n%s' % (mention_author, frame_str_3, u'\n----------------------------------------------------', frame_str_3)
            await message.edit(content=new_msg)

            await asyncio.sleep(0.25)

            if not is_gomi:
                new_msg = '%s\n%s%s\n%s' % (mention_author, frame_str_3, reply, frame_str_3)
                await message.edit(content=new_msg)
            else:
                await asyncio.sleep(1)
                await self.call_gomi_msg(mention_author, channel, message)

        else:
            # 通常演出
            frame_str = await self._get_frame_str('SR3')
            msg = '%s\n%s%s\n%s' % (mention_author, frame_str, u'\n----------------------------------------------------', frame_str)
            message = await channel.send(msg)

            await asyncio.sleep(1)

            if not is_gomi:
                new_msg = '%s\n%s%s\n%s' % (mention_author, frame_str, reply, frame_str)
                await message.edit(content=new_msg)
            else:
                await self.call_gomi_msg(mention_author, channel, message)

    async def call_ssr_msg(self, mention_author, channel, reply, is_gomi):
        production_value = random.randrange(100)
        if production_value >= 50:
            # 確定演出
            frame_str_r = await self._get_frame_str('Common')
            frame_str_1 = await self._get_frame_str('SSR1')
            frame_str_2 = await self._get_frame_str('SSR2')
            frame_str_3 = await self._get_frame_str('SSR3')
            frame_str_4 = await self._get_frame_str('SSR4')
            frame_str_5 = await self._get_frame_str('SSR5')
            frame_str_6 = await self._get_frame_str('SSR6')
            msg = '%s\n%s%s\n%s' % (mention_author, frame_str_r, u'\n----------------------------------------------------', frame_str_r)
            message = await channel.send(msg)

            await asyncio.sleep(1)

            new_msg = '%s\n%s%s\n%s' % (mention_author, frame_str_1, u'\n----------------------------------------------------', frame_str_1)
            await message.edit(content=new_msg)

            await asyncio.sleep(0.15)

            new_msg = '%s\n%s%s\n%s' % (mention_author, frame_str_2, u'\n----------------------------------------------------', frame_str_2)
            await message.edit(content=new_msg)

            await asyncio.sleep(0.15)

            new_msg = '%s\n%s%s\n%s' % (mention_author, frame_str_3, u'\n----------------------------------------------------', frame_str_3)
            await message.edit(content=new_msg)

            await asyncio.sleep(0.15)

            new_msg = '%s\n%s%s\n%s' % (mention_author, frame_str_4, u'\n----------------------------------------------------', frame_str_4)
            await message.edit(content=new_msg)

            await asyncio.sleep(0.15)

            new_msg = '%s\n%s%s\n%s' % (mention_author, frame_str_5, u'\n----------------------------------------------------', frame_str_5)
            await message.edit(content=new_msg)

            await asyncio.sleep(0.15)

            new_msg = '%s\n%s%s\n%s' % (mention_author, frame_str_6, u'\n----------------------------------------------------', frame_str_6)
            await message.edit(content=new_msg)

            await asyncio.sleep(0.15)

            if not is_gomi:
                new_msg = '%s\n%s%s\n%s' % (mention_author, frame_str_6, reply, frame_str_6)
                await message.edit(content=new_msg)
            else:
                await asyncio.sleep(1)
                await self.call_gomi_msg(mention_author, channel, message)

        else:
            # 通常演出
            frame_str = await self._get_frame_str('SSR6')
            msg = '%s\n%s%s\n%s' % (mention_author, frame_str, u'\n----------------------------------------------------', frame_str)
            message = await channel.send(msg)

            await asyncio.sleep(1)

            if not is_gomi:
                new_msg = '%s\n%s%s\n%s' % (mention_author, frame_str, reply, frame_str)
                await message.edit(content=new_msg)
            else:
                await self.call_gomi_msg(mention_author, channel, message)

    async def _get_frame_str(self, frame_type):
        frame = ''
        black  = ':black_circle: '
        brown  = ':brown_circle: '
        white  = ':white_circle: '
        red    = ':red_circle: '
        orange = ':orange_circle: '
        yellow = ':yellow_circle: '
        green  = ':green_circle: '
        blue   = ':blue_circle: '
        purple = ':purple_circle: '

        if frame_type == 'Gomi':
            for _ in range(6):
                frame += black
                frame += brown

        elif frame_type == 'Common':
            for _ in range(12):
                frame += brown

        elif frame_type == 'Rare':
            for _ in range(12):
                frame += white

        elif frame_type == 'SR1':
            frame += yellow
            for _ in range(10):
                frame += white
            frame += yellow

        elif frame_type == 'SR2':
            frame += orange
            frame += yellow
            for _ in range(8):
                frame += white
            frame += yellow
            frame += orange

        elif frame_type == 'SR3':
            frame += red
            frame += orange
            frame += yellow
            for _ in range(6):
                frame += white
            frame += yellow
            frame += orange
            frame += red

        elif frame_type == 'SSR1':
            for _ in range(5):
                frame += brown
            frame += purple
            frame += purple
            for _ in range(5):
                frame += brown

        elif frame_type == 'SSR2':
            for _ in range(4):
                frame += brown
            frame += blue
            frame += purple
            frame += purple
            frame += blue
            for _ in range(4):
                frame += brown

        elif frame_type == 'SSR3':
            for _ in range(3):
                frame += brown
            frame += green
            frame += blue
            frame += purple
            frame += purple
            frame += blue
            frame += green
            for _ in range(3):
                frame += brown

        elif frame_type == 'SSR4':
            for _ in range(2):
                frame += brown
            frame += yellow
            frame += green
            frame += blue
            frame += purple
            frame += purple
            frame += blue
            frame += green
            frame += yellow
            for _ in range(2):
                frame += brown

        elif frame_type == 'SSR5':
            frame += brown
            frame += orange
            frame += yellow
            frame += green
            frame += blue
            frame += purple
            frame += purple
            frame += blue
            frame += green
            frame += yellow
            frame += orange
            frame += brown

        elif frame_type == 'SSR6':
            frame += red
            frame += orange
            frame += yellow
            frame += green
            frame += blue
            frame += purple
            frame += purple
            frame += blue
            frame += green
            frame += yellow
            frame += orange
            frame += red

        return frame


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

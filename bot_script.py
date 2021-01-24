# -*- coding: utf-8 -*-

import os
import re
import random
import asyncio  
from collections import namedtuple
from functools import partial

from discord.ext import commands
import discord

ADMIN_USER_ID = '358579613670309888'

TOKEN_PW = os.environ['DISCORD_BOT_TOKEN_PW']
TOKEN_KUROMAKU = os.environ['DISCORD_BOT_TOKEN_KUROMAKU']
TOKEN_KURUKURU = os.environ['DISCORD_BOT_TOKEN_KURUKURU']
TOKEN_CHOGATH = os.environ['DISCORD_BOT_TOKEN_CHOGATH']

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
        elif message.content == '/一覧':
            await self.list_participants(message.channel)
            return
        elif message.content == '/人数':
            await self.appear_number(message.channel)
            return
        elif message.content.startswith('/募集'):
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
        elif self.user in message.mentions:
            user_is_admin = int(message.author.id) == int(ADMIN_USER_ID)
            if user_is_admin and ('/解体' in message.content):
                # 話しかけたのが管理者で「/解体」が含まれる場合
                await message.channel.send('さようなら...')
                await self.logout()
            else:
                # それ以外のメッセージ
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
        elif self.user in message.mentions:
            user_is_admin = int(message.author.id) == int(ADMIN_USER_ID)
            if user_is_admin and ('/解体' in message.content):
                # 話しかけたのが管理者で「/解体」が含まれる場合
                await message.channel.send('さようなら...')
                await self.logout()
            else:
                # それ以外のメッセージ
                await self.reply(message.channel, message.author)
            return
        elif 'くろまく' in message.content:
            await self.worship(message.channel)
            return
        elif 'あいきん' in message.content:
            await message.channel.send('あいきんって誰？どちらさん？')
            return
        elif 'アイキン' in message.content:
            await message.channel.send('アイキンって誰？どちらさん？')
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
                u'遊戯王': u'このカードが召喚に成功したとき、\n相手プレイヤーに8000Pのダメージを与える',
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

        reply = '\n%s\n[%s] %sくろまく\n\n%s' % (star, rank, msg_title, msg)

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
    
    async def worship(self, channel):
        """くろまくさんを崇拝する"""
        worship_list = [
            '神', '天才', '正義', '羅将', '英雄', 'ヒーロー', '王', '皇帝', '伝説',
            '素晴らしい', '美しい', 'すごい', '神々しい', 
            'イケボ', 'イケメン', 'プロゲーマー',
        ]
        rand = random.randrange(len(worship_list))
        worship_word = worship_list[rand]
        msg = 'くろまくさんは%s' % worship_word
        await channel.send(msg)

    async def call_gomi_msg(self, mention_author, channel, message):
        frame_str = await self._get_frame_str('Gomi')
        msg = '%s\n%s%s\n%s' % (mention_author, frame_str, u'\n----------------------------------------------------', frame_str)
        await message.edit(content=msg)

        await asyncio.sleep(1)

        reply = '\n%s\n[%s] %s\n\n%s' % ('★☆☆☆☆☆', 'Gomi', 'ごみりん', '残念！ごみりんが出ちゃった！')
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

class KuruKuruBot(discord.Client):

    async def on_ready(self):
        """起動時に呼ばれる"""
        # 起動したらターミナルにログイン通知が表示される
        print('Hello World')

    async def on_message(self, message):

        if message.author.bot:
            # メッセージ送信者がBotだった場合は無視する
            return
        elif self.user in message.mentions:
            # @メッセージ
            user_is_admin = int(message.author.id) == int(ADMIN_USER_ID)
            if user_is_admin and ('/解体' in message.content):
                # 話しかけたのが管理者で「/解体」が含まれる場合
                await message.channel.send('討伐完了! 80pt')
                await self.logout()
            else:
                # それ以外の@メッセージ
                await self.reply(message.channel, message.author)
            return

    async def reply(self, channel, author):
        """@で話しかけられた時の応答"""

        rank_value = random.randrange(100)
        if rank_value <= 44:
            # 0 - 44 (45%)
            rank = 1
        elif rank_value <= 74:
            # 45 - 74 (30%)
            rank = 2
        elif rank_value <= 89:
            # 75 - 89 (15%)
            rank = 3
        elif rank_value <= 96:
            # 90 - 96 (7%)
            rank = 4
        elif rank_value <= 99:
            # 97 - 99 (3%)
            rank = 5

        message = await self._get_message(rank)
        await self._call_message(author.mention, channel, rank, message)

    async def _get_message(self, rank):
        """@で話しかけられた時の応答メッセージを返す"""

        accessory_str = await self._get_accessory_str(rank)
        if not accessory_str:
            return

        stars = '★' * rank + '☆' * (5-rank)

        item_rank_dict = await self._get_item_rank_dict()

        item_dict = item_rank_dict[rank]

        rand = random.randrange(len(item_dict.keys()))
        item_name = list(item_dict.keys())[rand]
        detail = item_dict[item_name]

        return '%s[rare %s]\n%s\n%s\n\n%s' % (accessory_str, str(rank), stars, item_name, detail)

    async def _call_message(self, author, channel, rank, message_str):
        accessory_hatena = await self._get_accessory_str(-1)
        accessory = await self._get_accessory_str(rank)
        message = await channel.send('%s\n%s\nクルクル...' % (author, accessory_hatena))
        await asyncio.sleep(1)
        await message.edit(content='%s\n%s\nクルクル...クルクル...' % (author, accessory_hatena))
        await asyncio.sleep(1)

        if rank <= 3:
            # 通常演出
            is_slot = random.randrange(100) >= 80
            if is_slot:
                # ぬか喜び演出
                await message.edit(content='%s\n%s%s\nクルクル...クルクル...来ルカモ！？' % (author, accessory_hatena, ':interrobang:'))
                message_str = '来ませんｗｗｗｗｗｗｗｗｗｗｗｗｗｗｗｗｗｗｗ\n\n' + message_str
            else:
                # 通常演出
                await message.edit(content='%s\n%s\nクルクル...クルクル...クル？' % (author, accessory))
        elif rank:
            # 確変演出
            is_slot = random.randrange(100) >= 50
            if is_slot:
                # 確定slot演出
                await message.edit(content='%s\n%s%s\nクルクル...クルクル...来ルカモ！？' % (author, accessory_hatena, ':interrobang:'))
            else:
                # 確定演出
                await message.edit(content='%s\n%s\nクルクル...クルクル...クルルッ！？' % (author, accessory))

        await asyncio.sleep(2)
        await message.edit(content=message_str)

    async def _get_accessory_str(self, rank):
        if rank == -1:
            emoji_obj = await self._find_emoji('accessory_hatena')
        elif rank == 1:
            emoji_obj = await self._find_emoji('accessory_white')
        elif rank == 2:
            emoji_obj = await self._find_emoji('accessory_blue')
        elif rank == 3:
            emoji_obj = await self._find_emoji('accessory_orrange')
        elif rank == 4:
            emoji_obj = await self._find_emoji('accessory_red')
        elif rank == 5:
            emoji_obj = await self._find_emoji('accessory_yellow')
        return emoji_obj

    async def _find_emoji(self, emoji_name):
        for emoji in self.emojis:
            if emoji.name == emoji_name:
                return emoji

    async def _get_item_rank_dict(self):
        return {
            1: {
                # real
                '近江牛': '滋賀県名物 日本三大和牛',
                '信楽焼': '滋賀県名物 よくあるタヌキのアレ',
                'のっぺいうどん': '滋賀県の郷土料理 かつおと昆布の合わせ出汁にあんかけを絡めたうどん',
                'じゅんじゅ': '滋賀県の郷土料理 琵琶湖の湖魚をすき焼き風に煮込んだもの',
                'ひこにゃん': '滋賀県のゆるキャラ 御神体であるチョガスを差し置いて登場した',
                'ムーディ勝山': '滋賀県出身 右（東京）から来た者を左（大阪）へ受け流す滋賀県はまさに日本の中心',
                'GACKT': '滋賀県出身 滋賀県以外映す価値なし',
                'ハローワーク': 'お仕事お探しですか？',
                # LOL
                'ダガー': 'タワー下のCSにおすすめ',
                '0/7/0 yasuo': 'ブロンズ帯か、飽きないものだな(本人はアイアン1)',
                '25分変身青ケイン': 'これはわざとじゃない "計画"だ',
                'Teemoサポート': 'キノコがあるからワードは不要',
                'アイバーンサポート': 'カニを一瞬で食べれるのでワードは不要',
                'ヴェイン即ロックマン': '深夜帯にスポーン率が高く危険',
                'ねこばばマスターイー': 'AAが二回出る つまり...',
                '絶対に降りないyuumi': 'チャンピオンパッシブ消滅',
                'コントロールワード': '75Gって高くね？（ブロンズ脳）',
                '脅威おばさん': '骨身に沁みる教え（脅威をしてはいけないということ）をくれてやろう',
                # TFT
                '青バフグインソーバード': 'Teemo君とJhin君来たから君、もう帰っていいよ',
                '宇宙海賊4': '4になった頃には体力ミリ',
                'スーパーメカガレン': 'アーゴットに処刑されるガレン',
                # mhw
                'アステラジャーキー': '広域化口移しジャーキー',
                'イヌ': 'た～まにゃ～',
                '鳥になった小梅太夫': 'ハクチョーーーーーーーー（白鳥）',
                'ハチミツ': 'ください',
                '元気ドリンコ': 'モンスターエナg（ry',
                '割れた卵の跡': 'それは "奴" がいた痕跡',
                'ツィツィヤック': '卵も掘れないくそ雑魚同業者ｗｗｗ',
                '暇ん珠【1】': 'ゲームプレイ時間持続・極意',
                '毒瓶珠【3】': '大戦犯スロ3',
                # ProjectWinter'
                'トレイターチェスト': 'さっき暇んちゅさんが開けてました',
                # MinecraftDungeons
                'ハープクロスボウ': 'ハリケーンソナ！？',
                # Minecraft
                'コカトリス': '鳴き声がうるさい',
                '鉄インゴット': '「装備せよ」',
                '黒曜石': 'アイスバケツチャレンジ',
                'ネザーゲート': '[検索] ネザーゲート 音 うるさい 消す',
                'ジュークボックス': '初めて手に入ったダイヤはこれにするのがお勧め',
                'ダイヤの鍬': '実は耕す速度が速く...ないです',
                'サドル': '永遠の友となるだろう！ → 即乗り換え',
                'スイートベリー': '食べるときは空を向いてよく噛んでお食べください',
                'エンダーパール': '間違ってマグマに投げ込まないでね',
                'ニート村人': '緑の服にピンときたら殺処分',
                'ファントム': '睡眠不足には気をつけよう！',
                'ウシ': 'いきなりステーキ ご来店お待ちしております',
                'ピグリン': '貧乏人を許さない豚の鑑',
                'クリーパー': 'なんということでしょう！ 悲劇的ビフォーアフター',
                'テラコッタ': '近年コンクリートに建材の座を奪われつつある',
            },
            2: {
                # real
                '彦根城跡': '滋賀県の観光名所 別名「金亀城」',
                '延暦寺': '滋賀県の観光名所 天台宗総本山',
                '近江神宮': '滋賀県の観光名所 天智天皇ゆかりの地',
                '安土城跡': '滋賀県の観光名所 あの有名な信長が城を建てた滋賀県こそ日本の中心',
                'ウインドノーツ': '琵琶湖の空で伝説を生んだ男',
                # LOL
                'ウィッツエンド': 'Taricのコアビルド',
                'アイスボーンガントレット': 'Taricのコアビルド',
                'ヨネヤスオbot': '「対面レンジなのにgankないとかきついわ」',
                '7/0/10 yasuo': '100秒後に1v5で負けてAFKするyasuo',
                '青バフ': 'セトjg「ちょっとくらい、貰ってもバレへんか」',
                # TFT
                'ダスクリヴェン': 'サモリフの悪夢再現',
                '★4アフェリオス': 'タレットが本体',
                # mhw
                '大サシミウロコ': '伝説の黒龍 VS 魚の早食い競争',
                'キブクレペンギン': '捕まえた後はどうなるのか誰も知らない...',
                '退散玉': '正直キミ..."臭う"よ？',
                'クルルフェイク': '今日からキミもクルクルヤック',
                '掻鳥の飾り羽': 'コレクター垂涎の一品',
                'スリンガーの弾': 'これがお年弾ってかｗｗ',
                '達人珠【1】': 'みんな大好き見切り+1',
                '茸好珠【1】': '読み方は "たけよし" じゅ',
                # ProjectWinter
                '調理した人間の肉': '処理したトレイターの死体の上でキャンプファイヤー',
                '聖書': '聖者の名のもとに狂った動物を殺戮',
                # MinecraftDungeons
                'レッドストーンゴーレム': 'マルファイトのパクリ',
                # Minecraft
                'エンチャントテーブル': '30 虫特攻Ⅳ...?',
                'ダイヤのつるはし': '炭鉱夫の必需品',
                '耐火のポーション': '効果時間切れた頃に大体集中力も切れて死ぬ',
                'ネザークォーツ': '掘るだけで人生経験豊かになるパワーストーン',
                'アイアンゴーレム': 'モデルはラピュタの巨神兵',
                '風車型ブランチマイニング': 'teriiさんが考えたそうです',
                '火打石': '昨夜未明、村で火災が発生しました 現場には火打石を手に走り回る不審な人物が目撃されており...',
                'ウィザースケルトンの頭': '頭が3つ...来るぞ遊馬！',
                'ブレイズロッド': 'ポテトに見えるともっぱらの噂',
                'エンダーアイ': 'いのりのゆびわくらいの頻度で壊れる',
            },
            3: {
                # real
                '琵琶湖のおいしい水': '汲んで売れば大儲け',
                '琵琶湖博物館': 'テーマは「湖と人間」',
                'びわ湖テラス': '滋賀県の観光名所 インスタ映え',
                '新宿の金蔵': 'また行きたいですね もう潰れちゃったかｗｗ',
                # LOL
                'バロンナッシャー': 'バロンとファーム、どっちが大事なの！？',
                # TFT
                '選ばれしものyasuo': '過ちは繰り返される',
                # mhw
                '金の錬金チケット': 'BBAにスパチャ',
                '縄張り争いの跡': 'クルクルヤックは岩を持つと気が大きくなりディアブロスにも挑むらしい なお結果は...',
                '竜のナミダ': 'ぶっ飛ばしとかやめろよ！ クルクルヤック泣いてるだろ！',
                '撃龍槍': 'やったぜ。投稿者：変態糞狩人 (8月16日（水）07時14分22秒)',
                '超心珠【2】': 'ペンギン愛護団体激怒',
                # ProjectWinter
                'サバイバー支援物資': '死刑宣告',
                # MinecraftDungeons
                '弱化のドラ': 'ドラドラテングダケ 相手は死ぬ',
                # Minecraft
                '砂漠のピラミッド': '攻略の際は1階の中央のブロックを壊すといいですよ',
                '無限弓': '矢が無限になる原理は不明',
                'エンダーマントラップ': 'バランスこわれる',
                '修繕本を売る司書': 'このご時世でも就職先に困らなさそう',
                'シーランタン': '光源の王様',
            },
            4: {
                # real
                '琵琶湖深層水': '飲むと不老不死になります',
                # LOL
                'マルファイト': '石頭トヨク言ワレル',
                # TFT
                '大魔王ガリオ': 'リーシンに蹴飛ばされる大魔王',
                # mhw
                '大霊脈玉': '「殲滅の主はまた鐘を鳴らす」',
                '黒龍の邪眼': '抉った目玉で全身を着飾る変態',
                '超心・整備珠【4】': '令和の炭鉱夫が追い求めたもの',
                '匠珠Ⅱ【4】': '驚異の出現率0.10%',
                # ProjectWinter
                '自白剤': '▼トレイター ちょ、これはその...そう！私イエティなんd（撲殺',
                # Minecraft
                'エリトラ': 'ご入用の際はエンドシティのファッキンシップまで',
                'ビーコン': 'ダイヤブロックだけで起動する猛者募集中',
                '海底神殿': 'ガーディアンの追いAIMは最強',
            },
            5: {
                # LOL
                '琵琶湖のアレ': '南無南無南無南無南無...',
                'SKT T1 Faker': '「努力せずにランクで1位になった」',
                # mhw
                '鋼龍の尖角': 'クルクルヤック生誕のストーリー',
                'クルルヤック希少種': 'モンハンライズで実装予定',
                'クルルヤックの卵': '新たな伝説が生まれる...！',
            },
        }

class ChogathBot(discord.Client):

    async def on_ready(self):
        """起動時に呼ばれる"""
        # 起動したらターミナルにログイン通知が表示される
        print('南無南無南無...')

    async def on_message(self, message):

        if message.author.bot:
            # メッセージ送信者がBotだった場合は無視する
            return
        elif self.user in message.mentions:
            # @メッセージ
            user_is_admin = int(message.author.id) == int(ADMIN_USER_ID)
            if user_is_admin and ('/解体' in message.content):
                # 話しかけたのが管理者で「/解体」が含まれる場合
                await message.channel.send('討伐完了! 80pt')
                await self.logout()
            else:
                # それ以外の@メッセージ
                if message.guild.voice_client:
                    # 既にボイスチャンネルにいる
                    return
                await self.join_voice_channel(message.author)
                await self.speak_chogath(message.guild)
            return

    async def join_voice_channel(self, author):
        """Botをボイスチャンネルに入室させる"""
        voice_state = author.voice

        if (not voice_state) or (not voice_state.channel):
            # もし送信者がどこのチャンネルにも入っていないなら
            return

        await voice_state.channel.connect()

    async def leave_voice_channel(self, guild):
        """Botをボイスチャンネルから切断させる"""
        voice_client = guild.voice_client

        if not voice_client:
            return

        await voice_client.disconnect()

    async def speak_chogath(self, guild):
        await self.play(guild)

    async def play(self, guild):
        """指定された音声ファイルを流します。"""
        voice_client = guild.voice_client

        voice_value = random.randrange(100)

        if voice_value <= 59:
            # 0 - 59 (60%)
            dir_ = './sound/chogath/'
        elif voice_value <= 69:
            # 60 - 69 (10%)
            dir_ = './sound/malphite/'
        elif voice_value <= 79:
            # 70 - 79 (10%)
            dir_ = './sound/yasuo/'
        elif voice_value <= 89:
            # 80 - 89 (10%)
            dir_ = './sound/teemo/'
        elif voice_value <= 99:
            # 90 - 99 (10%)
            dir_ = './sound/zoe/'

        files = os.listdir(dir_)
        file_name = files[random.randrange(len(files))]

        ffmpeg_audio_source = discord.FFmpegPCMAudio(dir_ + file_name)
        voice_client.play(ffmpeg_audio_source)

        await asyncio.sleep(10)

        await self.leave_voice_channel(guild)


Entry = namedtuple('Entry', 'client event token')  
entries = [  
    Entry(client=ProjectWinterBot(), event=asyncio.Event(), token=TOKEN_PW),  
    Entry(client=KuromakuBot(), event=asyncio.Event(), token=TOKEN_KUROMAKU),
    Entry(client=KuruKuruBot(), event=asyncio.Event(), token=TOKEN_KURUKURU),
    Entry(client=ChogathBot(), event=asyncio.Event(), token=TOKEN_CHOGATH)
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

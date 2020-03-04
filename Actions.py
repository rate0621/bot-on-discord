import os, re
import random
from datetime import datetime, timedelta, timezone
import discord
import gspread

import common_lib.priconne_gacha_simulator.GachaSimulation as GachaSimulation
import common_lib.priconne_gacha_simulator.ImageGenerator  as ImageGenerator
import common_lib.Common as Common
import response.Priconne as Pri

import rate_twitter_tools.twitter_tools as TwitterTools


#ServiceAccountCredentials：Googleの各サービスへアクセスできるservice変数を生成します。
from oauth2client.service_account import ServiceAccountCredentials

class Actions:
  def __init__(self):
    self.res      = None
    self.res_type = None

  def check_and_response(self, req):
    here = os.path.join( os.path.dirname(os.path.abspath(__file__)))


    # スタンプを返す系以外のは初めにチェックする
    # おれ騎士、凸報告部屋
    if req.channel.id == '497391628831555584':
      JST = timezone(timedelta(hours=+9), 'JST')
      now = datetime.now(JST).strftime('%Y/%m/%d %H:%M:%S')
      if datetime.now(JST).strftime('%Y/%m/%d 03:00:00') <= now <= datetime.now(JST).strftime('%Y/%m/%d 04:59:59'):
        self.res_type = 'file'
        self.res      = here + "/static/priconne/amesu2/yohuke.png"

        return self.res_type, self.res


    # アメス教徒のチャンネルID
    #if req.channel.id == '504911147280105475': # 開発用
    # NOTE:
    # 497625108387594250 <-おれきし
    # 562570171173175296 <-青鯖

    if req.channel.id in ('497625108387594250', '562570171173175296'):
      if re.search('アメス', req.content):
#        files = os.listdir(here + "/static/priconne/amesu/")
#
#        self.res_type = 'file'
#        self.res      = here + "/static/priconne/amesu/" + files[random.randrange(len(files))]
        if not re.search('アメス様', req.content):
          self.res_type = 'text'
          self.res      = req.author.mention + '  ・・・誰に向かって口聞いてるの？'

        else:
          self.res_type = 'text'
          self.res      = req.author.mention + ' ' + random.choice(Pri.amesu_res)
          if re.search('草アアアアアア', self.res):
            self.res_type = 'file'
            self.res      = here + "/static/priconne/amesu/kusaaa.png"
  

        return self.res_type, self.res

    if re.match("^プリコネ\sガチャ", req.content):
      self.res_type = 'file'
      self.res      = self.priconne_gacha_roll10()

      return self.res_type, self.res

    elif re.match("^↑↑↓↓←→←→\sプリコネ\sガチャ", req.content):
      self.res_type = 'file'
      self.res      = self.priconne_gacha_god_roll10()

      return self.res_type, self.res

    elif re.match("^画像\s", req.content):
      self.res_type = 'text'
      self.res      = self.getImage(req.content)

      return self.res_type, self.res

    elif re.match("^プリコネ\s(.+)\sチャレンジ$", req.content):
      self.res_type = 'text'
      self.res      = self.priconne_gacha_challenge(req.content)

      return self.res_type, self.res

    elif re.match("^プリコネ\s所持キャラ", req.content):
      match = re.search("^プリコネ\s所持キャラ\s(.+)$", req.content)
      if match is None:
        target_user = re.search("(.+)#.*$", req.author)
      else:
        target_user = match.group(1)

      self.res_type = 'text'
      self.res      = self.have_characters(target_user)

      return self.res_type, self.res

    elif re.search('キョウカ', req.content):
      if not re.search('キョウカちゃん', req.content):
        self.res_type = 'text'
        self.res      = req.author.mention + ' は？きちんと「ちゃん」をつけなさいよ'

        return self.res_type, self.res
        
    elif re.match("^プリコネ\sアカリ", req.content):
      files = os.listdir(here + "/static/priconne/akari/")

      self.res_type = 'file'
      self.res      = here + "/static/priconne/akari/" + files[random.randrange(len(files))]

      return self.res_type, self.res

    elif re.match("^マルコフ\s(.+)$", req.content):
      self.res_type = 'text'
      self.res      = self.markov(req.content)

      return self.res_type, self.res


    # スタンプ系はこの下に記述していく

    # 連続でスタンプがでまくるとログが流れてしまったりと鬱陶しいので、
    # スタンプは5分間に1回しかださない
    last_stamp_time_fp = here + '/last_stamp_time.txt'
    with open(last_stamp_time_fp, mode='r') as fh:
        s = fh.read()
        if s == '':
            last_stamp_time = datetime.strptime('2014/01/01 00:00:00', '%Y/%m/%d %H:%M:%S')
        else:
            last_stamp_time = datetime.strptime(s, '%Y/%m/%d %H:%M:%S')

    now = datetime.now()
    if (now - last_stamp_time).total_seconds() >= 3600:
      for word_list in Pri.responses:
        for word in word_list.split(','):
          if re.search(word, req.content):
            self.res      = here + "/static/priconne/" + Pri.responses[word_list]
            self.res_type = 'file'

            with open(last_stamp_time_fp, mode='w') as fh:
              fh.write(datetime.now().strftime("%Y/%m/%d %H:%M:%S"))

            return self.res_type, self.res

    ## 絵文字系はこの下に記述
    if re.search('幼女', req.content):
      self.res_type = 'emoji'
      self.res      = ['you:478527842855026698', 'jo:478527811296952330']

      ## 507788854418210826 ペコ
      if re.match('507788854418210826', req.author.id):
        self.res_type = 'emoji'
        self.res      = ['tuho:478871148134924309']

      return self.res_type, self.res

    if re.match('454636015785869313', req.author.id):
      self.res_type = 'text'
      self.res      = '(´^ω^｀)ﾌﾞﾌｫwww'

      return self.res_type, self.res


    return self.res_type, self.res

  def priconne_gacha_roll10(self):
    gs = GachaSimulation.GachaSimulation()
    charactor_list = gs.roll10()

    ig = ImageGenerator.ImageGenerator()
    gacha_result_path = ig.gacha_result_generator(charactor_list)

    return gacha_result_path

  def priconne_gacha_god_roll10(self):
    gs = GachaSimulation.GachaSimulation()
    charactor_list = gs.god_roll10()

    ig = ImageGenerator.ImageGenerator()
    gacha_result_path = ig.gacha_result_generator(charactor_list)

    return gacha_result_path

  def getImage(self, text):
    match = re.search("^画像\s(.+)", text)
    image_name = match.group(1)

    cmn = Common.Common()
    image_url_list = cmn.getImageUrl(image_name, 1)

    return image_url_list[0]

  def priconne_gacha_challenge(self, text):
    match = re.search("^プリコネ\s(.+)\sチャレンジ$", text)
    chara_name = match.group(1)

    gs = GachaSimulation.GachaSimulation()
    challenge_count, message = gs.challenge(chara_name)

    return message


  def markov(self, text):
    match = re.search("^マルコフ\s(.+)$", text)
    twi_id = match.group(1)

    tt = TwitterTools.TwitterTools()
    markof_text = tt.tweet_markov_from_specific_user(twi_id)

    return markof_text


  def have_characters(self, target_user):
    #2つのAPIを記述しないとリフレッシュトークンを3600秒毎に発行し続けなければならない
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']

    TYPE           = os.getenv("GS_TYPE", "")
    CLIENT_EMAIL   = os.getenv("GS_CLIENT_EMAIL", "")
    PRIVATE_KEY    = os.getenv("GS_PRIVATE_KEY", "")
    PRIVATE_KEY_ID = os.getenv("GS_PRIVATE_KEY_ID", "")
    CLIENT_ID      = os.getenv("GS_CLIENT_ID", "")

    key_dict = {
      'type'          : TYPE,
      'client_email'  : CLIENT_EMAIL,
      'private_key'   : PRIVATE_KEY,
      'private_key_id': PRIVATE_KEY_ID,
      'client_id'     : CLIENT_ID,
    }

    credentials = ServiceAccountCredentials.from_json_keyfile_dict(key_dict, scope)

    #OAuth2の資格情報を使用してGoogle APIにログインします。
    gc = gspread.authorize(credentials)

    #共有設定したスプレッドシートキーを変数[SPREADSHEET_KEY]に格納する。
    SPREADSHEET_KEY = os.getenv("SPREADSHEET_KEY", "")

    #共有設定したスプレッドシートのシート1を開く
    worksheet = gc.open_by_key(SPREADSHEET_KEY).sheet1


    # キャラ数取得
    ## 空文字除去
    characters = worksheet.col_values(2)
    characters = [i for i in characters if i]

    chara_count = len(characters)

    # 対象ユーザのカラム取得
    _range = worksheet.range('C3:AE3')

    target_col = ''
    for i in _range:
      if i.value == target_user:
        target_col = i.col

    if target_col == '':
      return 'そんな人、あたしは知らないわ。シートの上に名前が存在するか確認したらどうかしら。'

    got_characters = worksheet.col_values(target_col)
    got_characters = [i for i in got_characters if i]
    got_characters.pop(0)

    if len(characters) == len(got_characters):
      not_jinken = 0
      message = '```'
      message += "☆が３以上のキャラのみを表示。\n"
      for (name, level) in zip(characters, got_characters):
        is_designated = ''
        if re.search('専', level):
          is_designated = '専'
          level = re.sub(r'\D', '', level)

        if not level == '-':
          if int(level) >= 3:
            #message += name + ':' + str(level) + 's%' + "\n" % is_designated
            message += name + ':' + str(level) + '%s' % is_designated + "\n"
        elif re.search('クリス', name):
          not_jinken = 1

      if not_jinken :
        message += 'クｗｗクｗｗｗクリスおりゃん奴ーーーｗｗｗｗｗくうううううううｗｗ'

      message += "\n\nもし更新したい場合はここからできるわよ。（育成相談のトピックにも貼ってあるわ）\n" + os.getenv("CHARA_SHEET", "")
      message += '```'

    else:
      message = "所持キャラ情報がまだ揃ってないみたいね。持っていないキャラは - で入力するのよ。（スプシへのリンクは育成相談のトピックにも貼られてあるわ）\n" + os.getenv("CHARA_SHEET", "")

    return message

if __name__ == '__main__':
  pass
#  act = Actions()
#  print (act.have_characters('チャット'))


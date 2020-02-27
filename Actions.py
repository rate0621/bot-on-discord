import os, re
import random
from datetime import datetime, timedelta, timezone
import discord

import common_lib.priconne_gacha_simulator.GachaSimulation as GachaSimulation
import common_lib.priconne_gacha_simulator.ImageGenerator  as ImageGenerator
import common_lib.Common as Common
import response.Priconne as Pri


class Actions:
  def __init__(self):
    self.res      = None
    self.res_type = None

  def check_and_response(self, req):
    here = os.path.join( os.path.dirname(os.path.abspath(__file__)))


    # スタンプを返す系以外のは初めにチェックする

    # アメス教徒のチャンネルID
    #if req.channel.id == '504911147280105475': # 開発用
    # NOTE:
    # 497625108387594250 <-おれきし
    # 562570171173175296 <-青鯖

    if req.channel.id in (497625108387594250, 562570171173175296, 509921936856449044):
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

    # スタンプ系はこの下に記述していく

    # 連続でスタンプがでまくるとログが流れてしまったりと鬱陶しいので、
    # スタンプは60分間に1回しかださない
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


if __name__ == '__main__':
  pass
#  act = Actions()
#  print (act.have_characters('チャット'))


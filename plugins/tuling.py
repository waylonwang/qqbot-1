# -*- coding: utf-8 -*-
import re
import requests
import time
from datetime import datetime
from qqbot import QQBot
from qqbot.utf8logger import INFO, CRITICAL, ERROR, DEBUG
from qqbot.common import JsonDumps, JsonLoads, HTMLUnescape, PY3

def onQQMessage(bot, contact, member, content):
    global tuling
    cmd = ''
    user_id = ''
    reply_prefix = ''
    if contact.ctype == 'group':
        # 群聊
        user_id = member.qq
        user_nick = member.card if member.card != '' else member.nick
        reply_prefix = tuling.getPrefix() + '@' + user_nick + ' '
        cmd = tuling.getCommand(contact.qq,user_id,content)
    elif contact.ctype == 'buddy':
        # 单聊
        user_id = contact.qq
        reply_prefix = tuling.getPrefix()
        cmd = tuling.getCommand(None,user_id,content)
    else:
        # 聊天组及临时聊天不支持
        pass

    if cmd == '':
        return None

    data = tuling.getMessage(cmd,user_id)
    bot.SendTo(contact, reply_prefix + data.get('text',''),False)
    DEBUG("[图灵消息](" + data.get('userid','') + ") " + data.get('text',''))
    pass


class TulingBot():
    __conf = None
    __url = 'http://www.tuling123.com/openapi/api'
    __headers = {'Content-Type': 'application/x-www-form-urlencoded',
               'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0'}
    __userCount = {}
    __lastChat = None

    def __init__(self,conf):
        self.__conf = {
            "api_key": self.__getConf(conf,'api_key'),
            "reply_prefix": self.__getConf(conf,'reply_prefix'),
            "maxcount_peruser": self.__getConf(conf,'maxcount_peruser'),
            "delay_perchat": self.__getConf(conf,'delay_perchat'),
            "whitelist": self.__getConf(conf,'whitelist'),
            "blacklist": self.__getConf(conf,'blacklist'),
            "command": self.__getConf(conf, 'command'),
        }
        self.__lastChat = datetime.now()

    def getMessage(self,cmd,userid):
        self.__delay()
        if self.__userCount.get(userid,0) > self.__conf.get('maxcount_peruser',0):
            return '你今天和我聊天的次数太多了，明天再陪你聊'
        else:
            info = {
                'key': self.__conf.get('api_key'),
                'info': cmd,
                'userid': userid
            }
            r = requests.post(self.__url,data=info,headers=self.__headers)
            if r.status_code == 200:
                r.encoding = 'utf-8'
                data = JsonLoads(r.text)
                code = str(data.get('code',''))
                if code == '100000':
                    retMessage = data.get('text','')
                elif code == '200000':
                    retMessage = data.text + ' ' + data.get('url','')
                elif code == '302000':
                    retMessage = '《' + data.list[0].article + '》 ' + data.get('detailurl','')
                elif code == '308000':
                    retMessage = '《' + data.list[0].name + '》 ' + data.get('detailurl','')
                elif code == '40001':
                    retMessage = '我出了点小故障，修复后再告诉你'
                    DEBUG('未发送正确的APIKEY给图灵')
                elif code == '40002':
                    retMessage = '我出了点小故障，修复后再告诉你'
                    DEBUG('未发送正确的info给图灵')
                elif code == '40004':
                    retMessage = '对不起，我已经休息了，明天再继续工作'
                elif code == '40007':
                    retMessage = '我出了点小故障，修复后再告诉你'
                    DEBUG('未发送正确的数据给图灵')
                else:
                    retMessage = '我出了点小故障，修复后再告诉你'

                self.__userCount[userid]=self.__userCount.get(userid,0)+1
                return {
                    'userid': info.get('userid',''),
                    'text': retMessage
                }
            else:
                DEBUG('未发送正确的数据给图灵')
                return '我出了点小故障，修复后再告诉你'
        pass

    def getCommand(self,group_act,user_act,content):
        # 过滤规则：处理群组->处理用户->处理关键词命令
        # 名单规则：处理白名单->处理黑名单
        if group_act is not None:
            # 群聊时应用所有规则
            # STEP1.处理白名单群组
            result = self.__matchRule(self.__conf.get('whitelist').get('group',''),group_act)
            if result == '': return ''
            # STEP2.处理黑名单群组
            result = self.__matchRule(self.__conf.get('blacklist').get('group',''),group_act)
            if result != '': return ''
            # STEP3.处理白名单用户
            result = self.__matchRule(self.__conf.get('whitelist').get('user',''),user_act)
            if result == '': return ''
            # STEP4.处理黑名单用户
            result = self.__matchRule(self.__conf.get('blacklist').get('user',''),user_act)
            if result != '': return ''
            # STEP5.处理关键词命令
            return self.__matchRule(self.__conf.get('command'),content)
        else:
            # 聊时不应用群组黑白名单、关键词处理规则
            # STEP1.处理白名单用户
            result = self.__matchRule(self.__conf.get('whitelist').get('user',''),user_act)
            if result == '': return ''
            # STEP2.处理黑名单用户
            result = self.__matchRule(self.__conf.get('blacklist').get('user',''),user_act)
            if result != '': return ''
            return content
        pass

    def getPrefix(self):
        return self.__conf.get('reply_prefix','')

    def __matchRule(self,rule,condition):
        '''
        Args:
            rule:匹配规则
            condition:输入条件
        '''
        try:
            m = re.match(r''+ rule,condition)
            return m.group(1)
        except:
            return ''
        pass

    def __getConf(self,conf,name):
        value = None
        try:
            value = conf.get('tuling.'+name)
        except:
            pass
        return value

    def __delay(self):
        delay = self.__conf.get('delay_perchat', 0) - (datetime.now() - self.__lastChat).seconds
        if delay > 0:
            time.sleep(delay)
        self.__lastChat = datetime.now()

tuling = TulingBot(QQBot._bot.conf.pluginsConf)
DEBUG('TULING-LOAD-COMPLETE')

# -*- coding: utf-8 -*-
import re
import time
from datetime import datetime
from abc import ABCMeta, abstractmethod
from qqbot import QQBot
from qqbot import QQBotSched as qqbotsched
from qqbot.utf8logger import INFO, CRITICAL, ERROR, DEBUG
from qqbot.common import JsonDumps, JsonLoads, HTMLUnescape, PY3


def onQQMessage(bot, contact, member, content):
    global scorebot
    if contact.ctype == 'group':
        # 群聊
        user_id = member.qq
        user_nick = member.card if member.card != '' else member.nick
        # reply_prefix = scorebot.getPrefix() + '@' + user_nick + ' '
        reply_prefix = ''
        retCmd = scorebot.execCommand(contact.qq, user_id, content)
    elif contact.ctype == 'buddy':
        # 单聊
        pass
    else:
        # 聊天组及临时聊天不支持
        pass
    if retCmd == '':
        return None
    bot.SendTo(contact, reply_prefix + retCmd, False)
    pass


class ScoreBot():
    __conf = None
    __commands = []
    __userCount = {}
    __lastChat = None

    def __init__(self,conf):
        self.__conf = {
            "reply_prefix": self.__getConf(conf,'reply_prefix'),
            "maxcount_peruser": self.__getConf(conf,'maxcount_peruser'),
            "delay_perchat": self.__getConf(conf,'delay_perchat'),
            "whitelist": self.__getConf(conf,'whitelist'),
            "blacklist": self.__getConf(conf,'blacklist'),
            "command": self.__getConf(conf, 'command'),
        }
        self.__commands = self.__conf['command']['commands']
        self.__lastChat = datetime.now()
        self.__registTask()

    def execCommand(self, group_act, user_act, content):
        if group_act is not None:
            # 群聊时应用所有规则
            # STEP1.处理白名单群组
            result = self.__matchRule(self.__conf.get('whitelist').get('group', ''), group_act).group(1)
            if result == '': return ''
            # STEP2.处理黑名单群组
            result = self.__matchRule(self.__conf.get('blacklist').get('group', ''), group_act).group(1)
            if result != '': return ''
            # STEP3.处理白名单用户
            result = self.__matchRule(self.__conf.get('whitelist').get('user', ''), user_act).group(1)
            if result == '': return ''
            # STEP4.处理黑名单用户
            result = self.__matchRule(self.__conf.get('blacklist').get('user', ''), user_act).group(1)
            if result != '': return ''
            # STEP5.处理关键词命令
            for command in self.__commands:
                try:
                    m = self.__matchRule(command['rule'],content)
                    if m.group(command.get('cmdindex',1)).strip() == command.get('cmd',):
                        params = []
                        for param in command['paramsindex']:
                            params.append(m.group(param))
                        # module = __import__("sb_recordtalk")
                        # cmd = module.Command()
                        # cmd._exec(user_act,str(params))
                        # className =
                        func = getattr(self, '_' + command['callfunc'])
                        if callable(func):
                            return func(user_act,str(params))
                        break
                except:
                    pass
            # return self.__matchRule(self.__conf.get('command'), content)
        else:
            pass
        pass

    def getPrefix(self):
        return self.__conf.get('reply_prefix', '')

    def _recordTalk(self,from_user,params):
        DEBUG("[ScoreBot记录发言]")
        return "查询发言 @" + from_user
        pass

    def _recordPoint(self,from_user,params):
        DEBUG("[ScoreBot记录报点]")
        pass

    def _recordPoint_confirm(self,from_user,params):
        DEBUG("[ScoreBot报点确认]")
        pass

    def _transitionDailyTalks(self,from_user,params):
        DEBUG("[ScoreBot转换发言]")
        pass

    def _transitionWeeklyPoints(self,from_user,params):
        DEBUG("[ScoreBot转换报点]")
        pass

    def __matchRule(self, rule, condition):
        '''
        Args:
            rule:匹配规则
            condition:输入条件
        '''
        try:
            return re.match(r'' + rule, condition)
        except:
            return ''
        pass

    def __getConf(self,conf,name):
        value = None
        try:
            value = conf.get('scorebot.'+name)
        except:
            pass
        return value

    def __delay(self):
        delay = self.__conf.get('delay_perchat', 0) - (datetime.now() - self.__lastChat).seconds
        if delay > 0:
            time.sleep(delay)
        self.__lastChat = datetime.now()

    def __registTask(self):
        # 注册定时任务
        for command in self.__commands:
            try:
                if command['schedule'] != '':
                    crons = self.__paraseCron(command['schedule'])
                    func = getattr(self, '_' + command['callfunc'])
                    if callable(func):
                        qqbotsched(second = crons['second'],
                                   minute = crons['minute'],
                                   hour = crons['hour'],
                                   day = crons['day'],
                                   month = crons['month'],
                                   day_of_week = crons['day_of_week'],
                                   year = crons['year'])(func)
            except:
                pass

    def __paraseCron(self,cron):
        fields = {'second':0,'minute':1,'hour':2,'day':3,'month':4,'day_of_week':5,'year':6}
        crons = {}
        cronlist = cron.split(' ')
        for (k,v) in fields.items():
            crons[k]=cronlist[v]
        return crons

class ScoreCommand():
    __metaclass__ = ABCMeta

    def __init__(self):
        self.command = ''

    @abstractmethod
    def _exec(self,from_user,params):pass

    def __str__(self):
        return str(self.command)

    def __repr__(self):
        return repr(self.command)

scorebot = ScoreBot(QQBot._bot.conf.pluginsConf)

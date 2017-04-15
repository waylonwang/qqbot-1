# -*- coding: utf-8 -*-
import re
import requests
from qqbot.utf8logger import INFO, CRITICAL, ERROR, DEBUG
from qqbot.common import JsonDumps, JsonLoads, HTMLUnescape, PY3


def onQQMessage(bot, contact, member, content):
    # TODO 增加对每人每天聊天限制次数
    # TODO 增加回复速度的控制
    if contact.ctype == "group":
        # 群聊
        user_id = member.qq
        user_nick = member.card if member.card != '' else member.nick
        reply_prefix = bot.conf.tuling_reply_prefix + '@' + user_nick + ' '
        cmd = getCommand(JsonLoads(bot.conf.tuling_whitelist),
                         JsonLoads(bot.conf.tuling_blacklist),
                         bot.conf.tuling_command,
                         contact.qq,
                         user_id,
                         content);
    elif contact.ctype == "buddy":
        # 单聊
        user_id = contact.qq
        user_nick = contact.card if contact.card != '' else contact.nick
        reply_prefix = bot.conf.tuling_reply_prefix + ' '
        cmd = getCommand(JsonLoads(bot.conf.tuling_whitelist),
                         JsonLoads(bot.conf.tuling_blacklist),
                         bot.conf.tuling_command,
                         None,
                         user_id,
                         content);
    else:
        # 聊天组及临时聊天不支持
        cmd = ''

    if cmd == '':
        return None

    info = {
        'key': bot.conf.tuling_api_key,
        'info': cmd,
        'userid': user_id
    }
    data = getMessage(info)
    bot.SendTo(contact, reply_prefix + data.get('text',''))
    DEBUG("[图灵消息](" + data.get('userid','') + ") " + data.get('text',''))


def getMessage(info):
    url = 'http://www.tuling123.com/openapi/api'
    headers = {'Content-Type': 'application/x-www-form-urlencoded',
               'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0'}
    r = requests.post(url,data=info,headers=headers)
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

        return {
            'userid': info.get('userid',''),
            'text': retMessage
        }
    else:
        DEBUG('未发送正确的数据给图灵')
        return None


def getCommand(whitelist,blacklist,command_rule,group_act,user_act,content):
    # 过滤规则：处理群组->处理用户->处理关键词命令
    # 名单规则：处理白名单->处理黑名单
    if group_act is not None:
        # 群聊时应用所有规则
        # STEP1.处理白名单群组
        result = matchRule(whitelist.get("group",""),group_act)
        if result == '': return ''
        # STEP2.处理黑名单群组
        result = matchRule(blacklist.get("group",""),group_act)
        if result != '': return ''
        # STEP3.处理白名单用户
        result = matchRule(whitelist.get("user",""),user_act)
        if result == '': return ''
        # STEP4.处理黑名单用户
        result = matchRule(blacklist.get("user",""),user_act)
        if result != '': return ''
        # STEP5.处理关键词命令
        return matchRule(command_rule,content)
    else:
        # 聊时不应用群组黑白名单、关键词处理规则
        # STEP1.处理白名单用户
        result = matchRule(whitelist.get("user",""),user_act)
        if result == '': return ''
        # STEP2.处理黑名单用户
        result = matchRule(blacklist.get("user",""),user_act)
        if result != '': return ''
        return content


def matchRule(rule,condition):
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


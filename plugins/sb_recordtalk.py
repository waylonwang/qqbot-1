# -*- coding: utf-8 -*-
from scorebot import ScoreCommand

class Command(ScoreCommand):
    def _exec(self,from_user,params):
        DEBUG("[ScoreBot记录发言]")
        return "查询发言 @" + from_user
        pass

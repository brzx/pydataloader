#!/usr/bin/python
# -*- coding: utf-8 -*-

import abc

class TargetTools():
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def getConnection(self, username, password, url):
        pass

    @abc.abstractmethod
    def validTarget(self, target):
        pass
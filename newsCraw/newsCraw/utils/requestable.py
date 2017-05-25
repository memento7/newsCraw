from scrapy.http import Request

from newsCraw import modules
from newsCraw.utils.connection import get_type_id

from datetime import datetime
from types import GeneratorType
from typing import Iterable
from collections import OrderedDict, defaultdict
import inspect

class Requestable:
    s = defaultdict(list)
    i = dict()
    def __init__(self, func):
        class_name, method_name = func.__qualname__.split('.')
        Requestable.s[class_name].append((method_name, func))
        self.func = func

    def __get__(self, obj, klass=None):
        def _call_ (*args, **kwargs):
            return self.func(obj, args, kwargs)
        return _call_

    @staticmethod
    def init():
        for module in modules.__all__:
            __import__(modules.dirname.replace('/', '.') + module)

        for cname, methods in Requestable.s.items():
            for fname, func in methods:
                module = inspect.getmodule(func)
                cls = getattr(module, cname)
                if not cname in Requestable.i:
                    Requestable.i[cname] = cls()
                    break

    @staticmethod
    def allow() -> Iterable[list]:
        for cls in Requestable.i.values():
            try:
                yield cls.allow
            except:
                continue

    @staticmethod
    def process(data: dict):
        for cname, methods in Requestable.s.items():
            for fname, method in methods:
                yield method(Requestable.i[cname], data)

    @staticmethod
    def dress(cname: str):
        return Requestable.i[cname].dressor

    @staticmethod
    def info(cname: str):
        return Requestable.i[cname].info

    @staticmethod
    def close():
        for name in list(Requestable.i):
            del Requestable.i[name]

from abc import ABCMeta, abstractmethod


class AbstractContext(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def tags(self):
        """
        Generate context-specific tags.

        :return: dict of tags
        """
        pass

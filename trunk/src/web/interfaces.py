from nevow.compy import Interface

class ITimer(Interface):
    """Timer interface, to bench rendering time"""

class ILastURL(Interface):
    """ Represents the last url visited """

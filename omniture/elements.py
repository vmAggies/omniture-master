# encoding: utf-8
from __future__ import absolute_import

from copy import copy
import logging

from .import utils


class Value(object):
    """ Searchable Dict. Can search on both the key and the value """
    def __init__(self, title, id, parent, extra={}):
        self.log = logging.getLogger(__name__)
        self.title = title.encode('utf-8')
        self.id = id
        self.parent = parent
        self.properties = {'id': id}

        for k, v in extra.items():
            setattr(self, k, v)

    @classmethod
    def list(cls, name, items, parent, title='title', id='id'):
        values = [cls(item[title], item[id], parent, item) for item in items]
        return utils.AddressableList(values, name)

    def __repr__(self):
        print self
        return "<{title}: {id} in {parent}>".format(**self.__dict__)

    def copy(self):
        value = self.__class__(self.title, self.id, self.parent)
        value.properties = copy(self.properties)
        return value

    def serialize(self):
        return self.properties

    def _repr_html_(self):
        """ Format in HTML for iPython Users """
        return "<td><b>{0}</b></td><td>{1}</td>".format(self.id, self.title)


    def __str__(self):
        """ allows users to print this out in a user friendly using print
        """
        return "ID {0:25} | Name: {1} \n".format(self.id, self.title)


class Element(Value):
    """ An element that you can use in the Reports to get data back """
    def range(self, *vargs):
        l = len(vargs)
        if l == 1:
            start = 0
            stop = vargs[0]
        elif l == 2:
            start, stop = vargs

        top = stop - start

        element = self.copy()
        element.properties['startingWith'] = str(start)
        element.properties['top'] = str(top)

        return element

    def search(self, keywords, type='AND'):
        type = type.upper()

        types = ['AND', 'OR', 'NOT']
        if type not in types:
            raise ValueError("Search type should be one of: " + ", ".join(types))

        element = self.copy()
        element.properties['search'] = {
            'type': type,
            'keywords': utils.wrap(keywords),
        }
        return element

    def select(self, keys):
        element = self.copy()
        element.properties['selected'] = utils.wrap(keys)
        return element


class Segment(Element):
    pass

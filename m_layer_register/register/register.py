#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © Her Majesty the Queen in Right of Canada, as represented
# by the Minister of Statistics Canada, 2019.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Copyright © 2022 Ryan Mackenzie White <ryan.white@nrc-cnrc.gc.ca>
#
# Distributed under terms of the Copyright © 2022 National Research Council Canada. license.

"""

"""
import collections
import fnmatch
from pathlib import Path
import uuid
import hashlib
import urllib.parse
from dataclasses import dataclass

from simplekv.fs import FilesystemStore

from m_layer_register.logger import Logger
from m_layer_register.model.mlayer_pb2 import DigitalObjectStore
from m_layer_register.model.mlayer_pb2 import DigitalObject

@dataclass
class MetaObject:
    """
    Helper data class for accessing a content object metadata
    The returned class does not give access to the original protobuf
    that is only accesible via uuid (content's hash)
    """

    name: str
    uuid: str
    parent_uuid: str
    address: str


class BaseBook(collections.abc.MutableMapping):
    """Base class for a collection of objects in a dictionary-like object.

    Attributes
    ----------
        _content : OrderedDict
            dictionary of histograms

    Parameters
    ----------
        hists : dict
            dictionary of histograms to initialize book
    """

    def __init__(self, hists={}):

        self._content = collections.OrderedDict()

        if isinstance(hists, dict):
            for n, x in hists.items():
                self[n] = x

        self._updated()

    @classmethod
    def load_from_dicts(cls, content):
        out = cls.__new__(cls)
        out._content = collections.OrderedDict()

        for k, v in content.items():
            out[k] = v

        return out

    def compatible(self, other):
        """
        books have equivalent keys
        re-implement in derived classes
        """

        return set(self._iter_keys()) == set(other._iter_keys())

    def _updated(self):
        pass

    def __eq__(self, other):
        """
        book1 == book2
        """
        return self.__class__ == other.__class__ and self._content == other._content

    def __ne__(self, other):
        """
        book1 != book2
        """
        return not self.__eq__(other)

    def __len__(self):
        """
        len(book)
        """
        return len(self._content)

    def __contains__(self, name):
        """
        if book has key
        """
        try:
            self[name]
        except KeyError:
            return False
        else:
            return True

    def _get(self, name):
        attempt = self._content.get(name, None)
        if attempt is not None:
            return attempt
        return None

    def __getitem__(self, name):
        if not isinstance(name, str):
            raise TypeError(
                "keys of a {0} must be strings".format(self.__class__.__name__)
            )

        if "*" in name:
            return [x for n, x in self if fnmatch.fnmatchcase(n, name)]
        else:
            out = self._get(name)
            if out is not None:
                return out
            else:
                raise KeyError(
                    "could not find {0} and could not interpret \
                                as a glob pattern".format(
                        repr(name)
                    )
                )

    def _set(self, name, value):
        self._content[name] = value
        self._updated()

    def __setitem__(self, name, value):
        """
        book[key] = value
        """

        if not isinstance(name, str):
            raise TypeError
        if not isinstance(value, HistogramBase):
            raise TypeError

        self._set(name, value)

    def _del(self, name):
        if name in self._content:
            del self._content[name]
            self._updated()
        else:
            raise KeyError

    def __delitem__(self, name):
        """
        del book[key]
        """
        if not isinstance(name, str):
            raise TypeError

        if "*" in name:
            keys = [n for n in self._contents.keys() if fnmatch.fnmatchcase(n, name)]
            for k in keys:
                self._del(k)
        else:
            self._del(name)

    def __iter__(self):
        """
        for k, v in book.items()
        """
        for k, v in self._content.items():
            yield k, v

    def _iter_keys(self):
        for k, v in self._content.items():
            yield k

    def _iter_values(self):
        for k, v in self._content.items():
            yield v

    def keys(self):
        return list(self._iter_keys())

    def values(self):
        return list(self._iter_values())

    def items(self):
        """
        book.items()
        """
        return list(self._content.items())

    def __add__(self, other):
        """
        book = book1 + book2
        """
        if not isinstance(other, BaseBook):
            raise TypeError("histogram books can only be added to other books")

        content = collections.OrderedDict()
        for n, x in self:
            if n in other:
                content[n] = x + other[n]
            else:
                content[n] = x
        for n, x in other:
            if n not in self:
                content[n] = x
        return self.__class__.load_from_dicts(content)

    def __iadd__(self, other):
        """
        book += book1
        """
        if not isinstance(other, BaseBook):
            raise TypeError("books can only be added to other books")

        for n, x in other:
            if n not in self:
                self[n] = x
            else:
                self[n] += x
        return self

@Logger.logged
class BaseObjectStore(BaseBook):
    """
    Base Object Store derives from an OrderedDict-like class
    """

    def __init__(
        self,
        root,
        name,
        store_uuid=None,
        storetype="hfs",
        algorithm="sha1",
        alt_root=None,
    ):
        """
        Loads a base store type
        Requires a root path where the store resides
        Create a store from persisted data
        Or create a new one
        """
        Logger.configure(self)
        self._mstore = DigitalObjectStore()
        self._dstore = FilesystemStore(f"{root}")
        self._alt_dstore = None
        if alt_root is not None:
            self.__logger.info("Create alternative data store location")
            self._alt_dstore = FilesystemStore(f"{alt_root}")
        self._algorithm = algorithm
        if store_uuid is None:
            # Generate a new store
            self.__logger.info("Generating new metastore")
            self._mstore.uuid = str(uuid.uuid4())
            self._mstore.name = f"{self._mstore.uuid}.{name}.cronus.pb"
            self._mstore.address = self._dstore.url_for(self._mstore.name)
            self._mstore.info.created.GetCurrentTime()
            self.__logger.info("Metastore ID %s", self._mstore.uuid)
            self.__logger.info("Storage location %s", self._mstore.address)
            self.__logger.info("Created on %s", self._mstore.info.created.ToDatetime())
        elif store_uuid is not None:
            self.__logger.info("Load metastore from path")
            self._load_from_path(name, store_uuid)
        else:
            self.__logger.error(
                "Cannot retrieve store: %s from datastore %s", store_uuid, root
            )
            raise KeyError

        self._name = self._mstore.name
        self._uuid = self._mstore.uuid
        self._parent_uuid = self._mstore.parent_uuid
        self._info = self._mstore.info
        self._aux = self._info.aux

        self._dups = dict()
        self._child_stores = dict()

        objects = dict()

        for item in self._info.objects:
            self.__logger.debug("Loading object %s", item.id)
            objects[item.id] = item

        super().__init__(objects)
    
    @property
    def store_name(self):
        return self._name

    @property
    def store_uuid(self):
        return self._uuid

    @property
    def store_info(self):
        return self._info

    @property
    def store_aux(self):
        return self._aux

    def _load_from_path(self, name, id_):
        self.__logger.info("Loading from path")
        print("Loading from path")
        try:
            buf = self._dstore.get(name)
        except FileNotFoundError:
            self.__logger.error("Metastore data not found")
            raise
        except Exception:
            self.__logger.error("Unknown error")
            raise

        self._mstore.ParseFromString(buf)
        if name != self._mstore.name:
            self.__logger.error(
                "Store name expected: %s received: %s", self._name, name
            )
            raise ValueError

    def save_store(self):
        buf = self._mstore.SerializeToString()
        self._dstore.put(self._mstore.name, buf)

    def register_content(self, content, info, **kwargs):
        """
        Returns a dataclass representing the content object
        content is the raw data, e.g. serialized bytestream to be persisted
        hash the bytestream, see for example github.com/dgilland/hashfs

        info object can be used to call the correct
        register method and validate all the required inputs are received
        """

        #metaobj = None
        dataset_id = kwargs.get("dataset_id", None)
        partition_key = kwargs.get("partition_key", None)
        job_id = kwargs.get("job_id", None)
        #  menu_id = kwargs.get('menu_id', None)
        #  config_id = kwargs.get('config_id', None)
        glob = kwargs.get("glob", None)

        content_type = type(content)
        if kwargs is not None:
            self.__logger.debug("Registering content %s", kwargs)
        
        self.__logger.debug("Register new dataset")
        obj = self._mstore.info.objects.add()
        obj.uuid = str(uuid.uuid4())  # Register new datsets with UUID4
        obj.parent_uuid = self._uuid
        obj.name = f"{obj.uuid}.dataset"
        obj.address = None #self._dstore.url_for(obj.name)
        self[obj.uuid] = obj
        return MetaObject(obj.name, obj.uuid, obj.parent_uuid, obj.address)
    
    def put(self, id_, content):
        """
        Writes data to kv store
        Support for:
        data wrapped as a pyarrow Buffer
        protocol buffer message

        Parameters
        ----------
        id_ : uuid of object
        content : pyarrow Buffer or protobuf msg

        Returns
        ----------
        """
        if type(content) is pa.lib.Buffer:
            try:
                self._put_object(id_, content)
            except Exception:
                raise
        else:
            try:
                self._put_message(id_, content)
            except Exception:
                raise
    def get(self, id_, msg=None):
        """
        Retrieves data from kv store
        Support for:
        pyarrow ipc file or stream
        pyarrow input_stream, e.g. csv, fwf, ...
        bytestream protobuf message

        Parameters
        ----------
        id_ : uuid of content
        msg : protobuf message to be parsed into

        Returns
        ---------
        In-memory buffer of data
        Deserialized protobuf message in python class instance

        Note:
            User must know protobuf message class to deserialize
        """

        if msg is None:
            return self._get_object(id_)
        else:
            self._get_message(id_, msg)
    
    def list(self, prefix="", suffix=""):
        objs = []
        for id_ in self.keys():
            if self[id_].name.startswith(prefix) and self[id_].name.endswith(suffix):
                self.__logger.debug(self[id_].name)
                objs.append(
                    MetaObject(
                        self[id_].name,
                        self[id_].uuid,
                        self[id_].parent_uuid,
                        self[id_].address,
                    )
                )
        return objs
    
    def _compute_hash(self, stream):
        hashobj = hashlib.new(self._algorithm)
        hashobj.update(stream.read())
        return hashobj.hexdigest()
    
    def __setitem__(self, id_, msg):
        """
        book[key] = value
        enfore immutible store
        """
        if id_ in self:
            self.__logger.error("Key exists %s", id_)
            raise ValueError
        if not isinstance(id_, str):
            raise TypeError
        if not isinstance(msg, DigitalObject):
            raise TypeError

        self._set(id_, msg)

    def _put_message(self, id_, msg):
        # proto message to persist
        self.__logger.debug("Putting message to datastore %s", self[id_].address)
        try:
            self._dstore.put(self[id_].name, msg.SerializeToString())
        except IOError:
            self.__logger.error("IO error %s", self[id_].address)
            raise
        except Exception:
            self.__logger.error("Unknown error put %s", self[id_].address)
            raise

    def _get_message(self, id_, msg):
        # get object will read object into memory buffer
        try:
            buf = self._dstore.get(self[id_].name)
            msg.ParseFromString(buf)
        except KeyError:
            self.__logger.error("Message not found in store %s", self[id_].address)
            raise

    def _put_object(self, id_, buf):
        # bytestream to persist
        self.__logger.debug("Putting buf to datastore %s", self[id_].address)
        try:
            self._dstore.put(self[id_].name, buf.to_pybytes())
        except IOError:
            self.__logger.error("IO error %s", self[id_].address)
            raise
        except Exception:
            self.__logger.error("Unknown error put %s", self[id_].address)
            raise

    def _get_object(self, id_):
        # get object will read object into memory buffer
        self.__logger.debug(self[id_])
        try:
            buf = self._dstore.get(self[id_].name)
        except KeyError:
            self.__logger.warning("Key not in store, try local %s", self[id_])
            # File resides outside of kv store
            # Used for registering files already existing in persistent storage
            buf = pa.input_stream(self._parse_url(id_)).read()
        except Exception:
            self.__logger.error("Key not in store, try local %s", self[id_])
        return buf

    def _parse_url(self, id_):
        url_data = urllib.parse.urlparse(self[id_].address)
        return urllib.parse.unquote(url_data.path)

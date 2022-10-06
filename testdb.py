#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2022 Ryan Mackenzie White <ryan.white@nrc-cnrc.gc.ca>
#
# Distributed under terms of the Copyright © 2022 National Research Council Canada. license.

"""

"""
import time
import bsddb3
import uuid
import json
import time
from functools import wraps
from m_layer_register.model.mlayerv2_pb2 import * 
from google.protobuf.json_format import MessageToJson


def timethis(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        r = func(*args, **kwargs)
        end = time.perf_counter()
        mytime = (end - start) / 1e-3
        return r, mytime
    return wrapper

def put_json(db, obj):
    jobj = MessageToJson(obj)
    _id = obj.id.value.encode()
    db[_id] = jobj

def put_pb(db, obj):
    do = DigitalObject()
    do.id = obj.id.value +".pb"
    do.type = obj.DESCRIPTOR.name
    do.content.Pack(obj)
    _id = do.id.encode()
    _str = do.SerializeToString()
    db[_id] = _str

@timethis
def get_json(db, _id):
    return json.loads(db[_id])

@timethis
def get_pb(db, _id):
    _mltype_mapper = {}
    _mltype_mapper["Aspect"] = Aspect
    _mltype_mapper["Reference"] = Reference 
    _mltype_mapper["Scale"] = Scale 
    _mltype_mapper["UnitSystem"] = UnitSystem 
    _mltype_mapper["ScalesForAspect"] = ScalesForAspect 
    _mltype_mapper["Conversion"] = Conversion 
    _mltype_mapper["Cast"] = Cast 
    _str = db[_id]
    obj = DigitalObject()
    obj.ParseFromString(_str)
    content = _mltype_mapper[obj.type]()
    obj.content.Unpack(content)
    return MessageToJson(content) 
    
def example():
    fn = 'example.db'
    db = bsddb3.hashopen(fn, 'c')
    t = time.time()
    _id = uuid.uuid4()
    print(str(_id))
    _idb = _id.bytes
    _id2 = uuid.UUID(bytes=_idb)
    print(str(_id2))

    a = Aspect()
    a.id.name = "aspect"
    #a.id.value = str(uuid.uuid4())
    a.id.value = str(12139911566084412692636353460656684046)
    a_json = MessageToJson(a)

    a_do = DigitalObject()
    a_do.id = a.id.value
    a_do.type = "Aspect"
    a_do.content.Pack(a)
    a_do_id = a_do.id + "_do.pb"
    a_do_str = a_do.SerializeToString()
    a_str = a.SerializeToString()
    print("Serialize Aspect")
    print(a_str)
    a_str_bytes = bytes(a_str)
    print("As bytes")
    print(a_str_bytes)
    ab = Aspect()
    ab.ParseFromString(a_str)
    print(ab.id.name)
    d = b"{data:'foo'}"
    db[_idb] = d
    db[a.id.value.encode()] = a_json
    print(a.id.value)
    ba = a.id.value.encode()
    ba2 = a.id.value + ".pb"
    ba2 = ba2.encode()
    db[ba2] = a_str
    db[a_do_id.encode()] = a_do_str
    print(ba.decode())
    print(db.keys())
    for k in db.keys():
        try:
            print(uuid.UUID(bytes=k))
        except:
            print(k.decode())

    print(db[_idb])
    print(db[ba])
    ac = db[ba2]
    ac_do = db[a_do_id.encode()]

    print(ac)
    ac2 = Aspect()
    ac2.ParseFromString(ac)
    ac_do2 = DigitalObject()
    ac_do2.ParseFromString(ac_do)
    print(ac2.id.name)
    print(ac_do2.id, ac_do2.type)
    ac3 = Aspect()
    ac_do2.content.Unpack(ac3)
    print(ac3.id.name)
    db.close()

if __name__ == "__main__":
    fn = 'example.db'
    db = bsddb3.hashopen(fn, 'c')
   
    example()
    a = Aspect()
    a.id.name = "aspect"
    a.id.value = str(uuid.uuid4())
    
    put_json(db, a)
    put_pb(db, a)

    msg1, t1 = get_json(db, a.id.value.encode())
    _idpb = a.id.value + ".pb"

    msg2, t2 = get_pb(db, _idpb.encode())
    
    print("Get the json artifact with time %4f ", t1)
    print(msg1)
    print("Get the Json from DO with time %4f ", t2)
    print(msg2)
    

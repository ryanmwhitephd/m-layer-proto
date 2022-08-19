#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2022 Ryan Mackenzie White <ryan.white@nrc-cnrc.gc.ca>
#
# Distributed under terms of the Copyright © 2022 National Research Council Canada. license.

"""

"""
from m_layer_register.model.mlayer_pb2 import *
from m_layer_register.register.register import BaseObjectStore 
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import MessageToDict

import uuid
import logging

def create_register():
    register = Register()
    register.name = "test"
    register.uuid = str(uuid.uuid4())

    mltemperature = register.aspects.add() 
    mltemperature.name = "temperature"
    mltemperature.uuid = str(uuid.uuid4())
    mltemperature.symbol = "T"

    mltempdiff = register.aspects.add()
    mltempdiff.name = "temperature-difference"
    mltempdiff.uuid = str(uuid.uuid4())
    mltempdiff.symbol = "dT"

    ml_si_kelvin_ratio = register.scales.add()
    ml_si_kelvin_ratio.name = "ml-si-kelvin-ratio"
    ml_si_kelvin_ratio.uuid = str(uuid.uuid4())
    ml_si_kelvin_ratio.scaletype = RATIO

    ml_si_celsius_interval = register.scales.add()
    ml_si_celsius_interval.name = "ml-si-celsius-interval"
    ml_si_celsius_interval.uuid = str(uuid.uuid4())
    ml_si_celsius_interval.scaletype = INTERVAL

    ml_si_kelvin_temperature = register.mobjects.add()
    ml_si_kelvin_temperature.name = "ml-si-kelvin-temperature"
    ml_si_kelvin_temperature.uuid = str(uuid.uuid4())
    aspect = ml_si_kelvin_temperature.aspect
    aspect = mltemperature
    scale = ml_si_kelvin_temperature.scale
    scale = ml_si_kelvin_ratio
    
    ml_si_celsius_temperature = register.mobjects.add()
    ml_si_celsius_temperature.name = "ml-si-celsius-temperature"
    ml_si_celsius_temperature.uuid = str(uuid.uuid4())
    aspect = ml_si_celsius_temperature.aspect
    aspect = mltemperature
    scale = ml_si_celsius_temperature.scale
    scale = ml_si_celsius_interval

    ml_si_celsius_kelvin_temperature = register.converters.add()
    ml_si_celsius_kelvin_temperature.uuid = str(uuid.uuid4())
    ml_si_celsius_kelvin_temperature.srcid = ml_si_celsius_temperature.uuid
    ml_si_celsius_kelvin_temperature.dstid = ml_si_kelvin_temperature.uuid
    ml_si_celsius_kelvin_temperature.dstid = ml_si_kelvin_temperature.uuid
    ml_si_celsius_kelvin_temperature.scaletype = INTERVAL
    ml_si_celsius_kelvin_temperature.nparms = 2
    ml_si_celsius_kelvin_temperature.parameters.append(1)
    ml_si_celsius_kelvin_temperature.parameters.append(273.15)

    msg = MLayerMsg()


    return register
    
def DOStore():
   
    store = DigitalObjectStore()
    sinfo = store.info
    store.name = "teststore.pb"
    store.uuid = str(uuid.uuid4())


    do = sinfo.objects.add()
    do.id = str(uuid.uuid4())

    mltemperature = AspectObject() 
    mltemperature.name = "temperature"
    mltemperature.uuid = str(uuid.uuid4())
    mltemperature.symbol = "T"

    do.type = mltemperature.DESCRIPTOR.name

    do.content.Pack(mltemperature)
    print(do.content)
    print(do.type)
    mltemp = AspectObject()
    print(do.content.Unpack(mltemp))
    print(MessageToJson(mltemp))

    for o in store.info.objects:
        print(do.id, do.type)

    fpath = "/home/rwhite/Projects/m-layer/m-layer-register/teststore.pb"
    f = open(fpath,"wb")
    f.write(store.SerializeToString())
    f.close()
    a_register = DigitalObjectStore()
    try:
        f = open(fpath, "rb")
        a_register.ParseFromString(f.read())
        f.close()
    except IOError:
        print("test.msg : Could not open file")
    for o in store.info.objects:
        print(do.id, do.type)

    a_store = BaseObjectStore(f"/home/rwhite/Projects/m-layer/m-layer-register", "teststore.pb", store.uuid)
    print(a_store[do.id].type)
    a_store[do.id].content.Unpack(mltemp)
    print(MessageToJson(mltemp))


class DigitalObjectWrapper():

    def __init__(self):
        _id = str(uuid.uuid4())
        _type = None
        _content = None
        _do = DigitalObject()

    def setContent(self):
        pass

    def getContent(self):
        pass


if __name__ == "__main__":

    register = create_register()
    print(register.name)
    print(register.aspects)
    print(register.scales) 
    print(register.mobjects)
    print("M Layer Converters")
    print(register.converters[0].uuid)
    print(register.converters[0].srcid)
    f = open("test.msg","wb")
    f.write(register.SerializeToString())
    f.close()

    a_register = Register()
    try:
        f = open("test.msg", "rb")
        a_register.ParseFromString(f.read())
        f.close()
    except IOError:
        print("test.msg : Could not open file")

    print(a_register.aspects)
    json_obj = MessageToJson(register)
    print(json_obj)

    dict_obj = MessageToDict(register)
    print(dict_obj)
    print(register.DESCRIPTOR.name)

    DOStore()


    

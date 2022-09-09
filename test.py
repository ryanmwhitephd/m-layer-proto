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
import json
from m_layer_register.logger import Logger

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

    print("Test the Register")
    a_store = BaseObjectStore(f"/home/rwhite/Projects/m-layer/m-layer-register", "teststore.pb", store.uuid, loglevel="debug")
    print("Object type: ", a_store[do.id].type, " id: ", do.id)
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

def aspect_to_dict(aspect):
    adict = {}
    adict["__entry__"] = aspect.DESCRIPTOR.name
    adict["uid"] = [aspect.identifier, aspect.uuid]
    adict["locale"] = {'default':
            {"name":aspect.name,"symbol":aspect.symbol}}
    print(json.dumps(adict, indent=2))

def aspectv2_to_dict(aspect):
    adict = {}
    adict["__entry__"] = aspect.DESCRIPTOR.name
    adict["uid"] = [aspect.id.name, aspect.id.value]
    adict["locale"] = {aspect.context.locale:
            {"name":aspect.context.name,"symbol":aspect.context.symbol}}
    print(json.dumps(adict, indent=2))

def aspects():
    mltemperature = AspectObject() 
    mltemperature.identifier = "ml_temperature" 
    mltemperature.uuid = str(uuid.uuid4())
    mltemperature.locale = "default"
    mltemperature.name = "temperature"
    mltemperature.symbol = "T"
    print(MessageToDict(mltemperature))
    
    mltempdiff = AspectObject()
    mltempdiff.identifier = "ml_temperature_difference"
    mltempdiff.name = "temperature-difference"
    mltempdiff.uuid = str(uuid.uuid4())
    mltempdiff.symbol = "dT"
    mltempdiff.locale = "default"
    print(MessageToDict(mltempdiff))

    mltorque = AspectObject()
    mltorque.identifier = "ml_torque"
    mltorque.uuid = str(uuid.uuid4())
    mltorque.locale = "default"
    mltorque.name = "torque"
    mltorque.symbol = "M"
    print(json.dumps(MessageToDict(mltorque),indent=2))
    aspect_to_dict(mltorque)

    mltorquev2 = AspectObjectv2()

    mltorquev2.id.name = "ml_torque"
    mltorquev2.id.value = str(uuid.uuid4())
    mltorquev2.id.type = "uuid4"
    mltorquev2.context.locale = "default"
    mltorquev2.context.name = "torque"
    mltorquev2.context.symbol = "M"
    print(json.dumps(MessageToDict(mltorquev2),indent=2))
    aspectv2_to_dict(mltorquev2)

def references():
    si_celsius = ReferenceObject()
    si_celsius.identifier = "si_celsius"
    si_celsius.uuid = str(uuid.uuid4())
    si_celsius.locale = "default"
    si_celsius.name = "celsius"
    si_celsius.symbol = "degree C"
    si_celsius.alternateid = "Cel"
    si_celsius.alternateid_type = "UCUM"
    si_celsius.alternateid_description = "degree Celsius"
    print(MessageToDict(si_celsius))

    si_becquerel = ReferenceObject()
    si_becquerel.identifier = "si_becquerel"
    si_becquerel.uuid = str(uuid.uuid4())
    si_becquerel.locale = "default"
    si_becquerel.name = "becquerel"
    si_becquerel.symbol = "Bq"
    si_becquerel.system_id = "si_system"
    si_becquerel.system_uuid = str(uuid.uuid4()) #Requires the actual uuid of the system that is registered 
    si_becquerel.dimensions.extend([0,0,-1,0,0,0,0])
    si_becquerel.prefix = 1
    si_becquerel.alternateid = "Bq"
    si_becquerel.alternateid_type = "UCUM"
    si_becquerel.alternateid_description = "becquerel"
    print(json.dumps(MessageToDict(si_becquerel),indent=2))

    si_becquerel = ReferenceObjectv2()
    si_becquerel.id.name = "si_becquerel"
    si_becquerel.id.value = str(uuid.uuid4())
    si_becquerel.id.type = "uuid4"
    si_becquerel.context.locale = "default"
    si_becquerel.context.name = "becquerel"
    si_becquerel.context.symbol = "Bq"
    si_becquerel.system_id.name = "si_system"
    si_becquerel.system_id.value = str(uuid.uuid4()) #Requires the actual uuid of the system that is registered 
    si_becquerel.dimensions.extend([0,0,-1,0,0,0,0])
    si_becquerel.prefix = 1
    si_becquerel.alternate_id.value = "Bq"
    si_becquerel.alternate_id.type = "UCUM"
    si_becquerel.alternate_id.description = "becquerel"
    print(json.dumps(MessageToDict(si_becquerel),indent=2))
if __name__ == "__main__":
    
    logging.getLogger().setLevel(logging.INFO)
    logging.info("Register Example")
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
    
    aspects()
    references()

    

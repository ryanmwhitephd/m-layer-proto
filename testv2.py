#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2022 Ryan Mackenzie White <ryan.white@nrc-cnrc.gc.ca>
#
# Distributed under terms of the Copyright © 2022 National Research Council Canada. license.

"""

"""
import uuid
import json
import jsonschema
import glob
import argparse
import os
import logging
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import MessageToDict

from m_layer_register.model.mlayerv2_pb2 import * 
from m_layer_register.logger import Logger
from m_layer_register.register.register import BaseObjectStore

#from m_layer.context import global_context as ctx
from m_layer.context import Context
from m_layer.expression import expr, value
from m_layer.uid import UID

@Logger.logged
class Mapper():

    def __init__(self, 
            store, 
            register, 
            context,
            path_to_schema,loglevel):
        self.store = store
        self.register = register
        self.context = context # M-layer context
        self.path_schema = path_to_schema
        Logger.configure(self,loglevel=loglevel)
        
        self.scale_type = {}
        self.scale_type["ratio"] = ScaleType.RATIO
        self.scale_type["interval"] = ScaleType.INTERVAL
        self.scale_type["ordinal"] = ScaleType.ORDINAL
        self.scale_type["bounded"] = ScaleType.BOUNDED
        self.scale_type[ScaleType.RATIO] = "ratio"
        self.scale_type[ScaleType.INTERVAL] = "interval"
        self.scale_type[ScaleType.ORDINAL] = "ordinal"
        self.scale_type[ScaleType.BOUNDED] = "bounded"
        
        self.type_mapper = {}
        self.type_mapper["Aspect"] = self.dict_to_aspect
        self.type_mapper["Reference"] = self.dict_to_reference
        self.type_mapper["Scale"] = self.dict_to_scale
        self.type_mapper["UnitSystem"] = self.dict_to_system
        self.type_mapper["ScalesForAspect"] = self.dict_to_scalesfor
        self.type_mapper["Conversion"] = self.dict_to_conversion
        self.type_mapper["Cast"] = self.dict_to_cast
        
        self.mltype_mapper = {}
        self.mltype_mapper["Aspect"] = self.aspect_to_dict
        self.mltype_mapper["Reference"] = self.reference_to_dict
        self.mltype_mapper["Scale"] = self.scale_to_dict
        self.mltype_mapper["UnitSystem"] = self.system_to_dict
        self.mltype_mapper["ScalesForAspect"] = self.scalesfor_to_dict
        self.mltype_mapper["Conversion"] = self.conversion_to_dict
        self.mltype_mapper["Cast"] = self.cast_to_dict

        self.type_schema = {}
        for key in self.type_mapper:
            self.type_schema[key] = self.load_jsonschema(key)
    
    def load_jsonschema(self, mltype):
        #path = "/home/rwhite/Projects/m-layer/m-layer-proto/m_layer_register/format/"
        self.__logger.info("Loading json schema from %s", self.path_schema)
        with open(self.path_schema+mltype+".json") as f:
            schema = json.load(f)
        return schema

    def add_object(self, mlobject):

        do = self.store.info.objects.add()
        do.id = mlobject.id.value
        do.type = mlobject.DESCRIPTOR.name
        do.content.Pack(mlobject)

        dop = self.register.register_content(mlobject)
   
    def validate(self, ref, test):
        self.__logger.debug("Validate")
        if ref != test:
            self.__logger.error("Cannot validate objects")
            self.__logger.error("Reference: ") 
            self.__logger.error(ref)
            self.__logger.error("Test: ")
            self.__logger.error(test)
            raise Exception
    
    def validate_as_json(self, mlobj):
        try:
            jsonschema.validate(instance=json.loads(MessageToJson(mlobj)),schema=self.type_schema[mlobj.DESCRIPTOR.name])
        except jsonschema.exceptions.ValidationError as err:
            self.__logger.error(err)
            err = "Given JSON data is Invalid"
            return False, err
        message = "Given JSON data is valid"
        return True, message

    def map_to_mlproto(self, refobj):
        self.__logger.debug(refobj)
        mlobj = self.type_mapper[refobj["__entry__"]](refobj)
        self.__logger.debug(MessageToJson(mlobj))
        is_valid, msg = self.validate_as_json(mlobj)
        obj = self.mltype_mapper[mlobj.DESCRIPTOR.name](mlobj)
        self.validate(refobj, obj)
        self.add_object(mlobj)
        self.context._load_entity(obj)


    def dict_to_aspect(self, obj):
        mlobj = Aspect()
        mlobj.id.name = obj["uid"][0] 
        mlobj.id.value = str(obj["uid"][1])
        mlobj.id.type = "uuid4"
        for key in obj["locale"]:
            context = mlobj.context.add()
            context.locale = key 
            context.name = obj["locale"][key]["name"]
            context.symbol = obj["locale"][key]["symbol"]
        if "metadata" in obj.keys():
        #    alt_id = mlobj.alternate_id.add() 
        #    alt_id.name = "Wikipedia"
        #    alt_id.value = obj['metadata']['url']
        #    alt_id.type = 'url'
            for key in obj['metadata']:
                mlobj.metadata[key] = obj['metadata'][key]
       
        return mlobj

    def aspect_to_dict(self, mlobj):
        obj = {}
        obj["__entry__"] = mlobj.DESCRIPTOR.name
        obj["uid"] = [mlobj.id.name, int(mlobj.id.value)]
        for ctx in mlobj.context:
            obj["locale"] = {ctx.locale: {"name":ctx.name, "symbol":ctx.symbol}}
        if len(mlobj.metadata.keys()) != 0:
            obj['metadata'] = {}
            for key in mlobj.metadata: 
                obj['metadata'][key] = mlobj.metadata[key]
        
        return obj
    
    def dict_to_reference(self, obj):
        mlobj = Reference()
        mlobj.id.name = obj["uid"][0]
        mlobj.id.value = str(obj["uid"][1])
        self.__logger.debug("Reference object id: %s ", mlobj.id.value)
        mlobj.id.type = "uuid4"
        self.__logger.debug(obj.keys()) 
        for key in obj["locale"]:
            context = mlobj.context.add()
            context.locale = key
            if "name" in obj["locale"][key]:
                context.name = obj["locale"][key]["name"]
            context.symbol = obj["locale"][key]["symbol"]
        
        if "system" in obj.keys():
            dims = obj["system"]["dimensions"]
            self.__logger.debug("Dimensions from dict %s %s", dims, type(dims))
            dims = eval(dims)
            self.__logger.debug("Dimensions from dict %s %s", dims, type(dims))
            system = mlobj.system.add()
            system.id.name = obj["system"]["uid"][0]
            system.id.value = str(obj["system"]["uid"][1])
            system.dimensions.extend(eval(obj["system"]["dimensions"]))
            system.prefix.extend(obj["system"]["prefix"])
        if "UCUM" in obj.keys(): 
            alternate_id = mlobj.alternate_id.add()
            alternate_id.value = obj["UCUM"]["code"]
            alternate_id.type = "UCUM"
            alternate_id.description = obj["UCUM"]["description"]
        if 'systematic' in obj.keys():
            self.__logger.debug("obj has systematic field")
            mlobj.systematic = bool(obj["systematic"])
            self.__logger.debug(mlobj.systematic)
       
        
        return mlobj

    def reference_to_dict(self, mlobj):
        obj = {}
        obj["__entry__"] = mlobj.DESCRIPTOR.name
        obj["uid"] = [mlobj.id.name,int(mlobj.id.value)]
        self.__logger.debug("Reference mlobject id: %s ", mlobj.id.value)
        obj['locale'] = {}
        for ctx in mlobj.context:
            if ctx.name == '':
                obj["locale"][ctx.locale] = {"symbol":ctx.symbol}
            else:
                obj["locale"][ctx.locale] = {"name":ctx.name, "symbol":ctx.symbol}
        for sys in mlobj.system:
            obj["system"] = {"uid":[sys.id.name, int(sys.id.value)],
                        "dimensions":str(sys.dimensions),
                        "prefix":sys.prefix}
        for alt in mlobj.alternate_id:
            obj["UCUM"] = {"code":alt.value,"description":alt.description}
        try:
            if mlobj.systematic is True:
                self.__logger.debug("mlobj has systematic field")
                obj['systematic'] = int(mlobj.systematic)
        except ValueError:
            self.__logger.error("systematic field not present")
        
        return obj
    
    def dict_to_scale(self, obj):
        self.__logger.debug(obj)
        mlobj = Scale()
        mlobj.id.name = obj["uid"][0] 
        mlobj.id.value = str(obj["uid"][1])
        mlobj.id.type = "uuid4"
        mlobj.reference_id.name = obj["reference"][0] 
        mlobj.reference_id.value = str(obj["reference"][1])
        mlobj.scaletype = self.scale_type[obj["scale_type"]]
        if 'systematic' in obj.keys():
            mlobj.systematic = obj["systematic"]
        return mlobj

    def scale_to_dict(self, mlobj):
        obj = {}
        obj["__entry__"] = mlobj.DESCRIPTOR.name
        obj["uid"] = [mlobj.id.name, int(mlobj.id.value)]
        obj["reference"] = [mlobj.reference_id.name, int(mlobj.reference_id.value)]
        obj["scale_type"] = self.scale_type[mlobj.scaletype]
        if(mlobj.systematic) is True:
            obj['systematic'] = int(mlobj.systematic)
        return obj
    
    def dict_to_system(self, obj):
        mlobj = UnitSystem()
        mlobj.id.name = obj["uid"][0]
        mlobj.id.value = str(obj["uid"][1])
        mlobj.name = obj["name"]
        
        for basis in obj["basis"]:
            base = mlobj.basis.add()
            base.name = basis[0]
            base.value = str(basis[1])
        
        return mlobj

    def system_to_dict(self, mlobj):
        obj = {}
        obj["__entry__"] = mlobj.DESCRIPTOR.name
        obj["uid"] = [mlobj.id.name, int(mlobj.id.value)]
        obj["name"] = mlobj.name
        obj["basis"] = []
        for basis in mlobj.basis:
            obj["basis"].append([basis.name, int(basis.value)])
       
        return obj
    
    def dict_to_scalesfor(self, obj):
        # Identifier required, how to compose?
        mlobj = ScalesForAspect()
        mlobj.id.value = str(uuid.uuid4())
        mlobj.aspect_id.name = obj["aspect"][0]
        mlobj.aspect_id.value = str(obj["aspect"][1])
        mlobj.src_id.name = obj["src"][0]
        mlobj.src_id.value = str(obj["src"][1])
        mlobj.dst_id.name = obj["dst"][0]
        mlobj.dst_id.value = str(obj["dst"][1])
        mlobj.function = obj["function"]
        for key in obj["parameters"]:
            mlobj.parameters[key] = obj["parameters"][key]
        #mlobj.factors.extend(obj["factors"])
        
        return mlobj

    def scalesfor_to_dict(self, mlobj):
        obj = {}
        obj["__entry__"] = mlobj.DESCRIPTOR.name
        obj["aspect"] = [mlobj.aspect_id.name, int(mlobj.aspect_id.value)]
        obj["src"] = [mlobj.src_id.name, int(mlobj.src_id.value)]
        obj["dst"] = [mlobj.dst_id.name, int(mlobj.dst_id.value)]
        obj["function"] = mlobj.function
        obj["parameters"] = {}
        for key in mlobj.parameters:
            obj["parameters"][key] = mlobj.parameters[key]
        #obj["factors"] = []
        #for f in mlobj.factors: obj["factors"].append(f)
        
        return obj

    def dict_to_conversion(self,obj):
        # Identifiers for conversion
        # Generate new ids or compose from src and dst identifiers
        mlobj = Conversion()
        mlobj.id.value = str(uuid.uuid4())
        mlobj.src_id.name = obj["src"][0]
        mlobj.src_id.value = str(obj["src"][1])
        mlobj.dst_id.name = obj["dst"][0]
        mlobj.dst_id.value = str(obj["dst"][1])
        mlobj.function = obj["function"]
        for key in obj["parameters"]:
            mlobj.parameters[key] = obj["parameters"][key]
        #mlobj.factors.extend(obj["factors"])
        
        #mlobj.id.value = mlobj.src_id.value + "_" + mlobj.dst_id.value         
        return mlobj

    def conversion_to_dict(self, mlobj):
        obj = {}
        obj["__entry__"] = mlobj.DESCRIPTOR.name
        obj["src"] = [mlobj.src_id.name, int(mlobj.src_id.value)]
        obj["dst"] = [mlobj.dst_id.name, int(mlobj.dst_id.value)]
        obj["function"] = mlobj.function
        obj["parameters"] = {}
        for key in mlobj.parameters:
            obj["parameters"][key] = mlobj.parameters[key]
        #obj["factors"] = []
        #for f in mlobj.factors: obj["factors"].append(f)
        
        return obj

    def dict_to_cast(self, obj):
        mlobj = Cast()
        mlobj.id.value = str(uuid.uuid4())
        mlobj.src_scale_id.name = obj["src"][0][0]
        mlobj.src_scale_id.value = str(obj["src"][0][1])
        mlobj.src_aspect_id.name = obj["src"][1][0]
        mlobj.src_aspect_id.value = str(obj["src"][1][1])
        mlobj.dst_scale_id.name = obj["dst"][0][0]
        mlobj.dst_scale_id.value = str(obj["dst"][0][1])
        mlobj.dst_aspect_id.name = obj["dst"][1][0]
        mlobj.dst_aspect_id.value = str(obj["dst"][1][1])
        mlobj.function = obj["function"]
        for key in obj["parameters"]:
            mlobj.parameters[key] = obj["parameters"][key]
        
        return mlobj

    def cast_to_dict(self,mlobj):
        obj = {}
        obj["__entry__"] = mlobj.DESCRIPTOR.name
        obj["src"] = [ [mlobj.src_scale_id.name, int(mlobj.src_scale_id.value)],
            [mlobj.src_aspect_id.name, int(mlobj.src_aspect_id.value)]]  
        obj["dst"] = [ [mlobj.dst_scale_id.name, int(mlobj.dst_scale_id.value)],
            [mlobj.dst_aspect_id.name,int(mlobj.dst_aspect_id.value)]]
        obj["function"] = mlobj.function
        obj["parameters"] = {}
        for key in mlobj.parameters:
            obj["parameters"][key] = mlobj.parameters[key]
        
        return obj



if __name__ == "__main__":
   
    logging.getLogger().setLevel(logging.INFO)
    logging.info("Register Example")
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', help="Input path to json files", action="store", dest="input")
    parser.add_argument('--loglevel', help="Logging level", action="store", dest="loglevel")
    args = parser.parse_args()
    mlayerpath = os.path.abspath(args.input + "/m-layer-concept/m_layer/json")
    path_to_schema = args.input+"/m-layer-proto/m_layer_register/format/"
    store = DigitalObjectStore()
    sinfo = store.info
    store.id.name = "teststore.pb"
    store.id.value = str(uuid.uuid4())
    store.id.type = "uuid4"
   
    register = BaseObjectStore("/tmp", "test")
    context = Context()
    mapper = Mapper(store, register, context, path_to_schema,loglevel=args.loglevel)
    #mapper.__logger.setLevel(logging.DEBUG)
    
    mltypes = ["aspects", "references", "scales", "scales_for", "systems"] 
    for _type in mltypes:
        for name in glob.glob(mlayerpath+"/"+_type + "/*"):
            try:
                with(open(name) as f):
                    data = json.load(f)
            except:
                print("error")
            for l_i in data:
                mapper.map_to_mlproto(l_i)
    for name in glob.glob(mlayerpath+"/conversion/*"):
        try:
            with(open(name) as f):
                data = json.load(f)
        except:
            print("error")
        for l_i in data:
            mapper.map_to_mlproto(l_i)
    for name in glob.glob(mlayerpath+"/casting/*"):
        try:
            with(open(name) as f):
                data = json.load(f)
        except:
            print("error")
        for l_i in data:
            mapper.map_to_mlproto(l_i)

    with open(mlayerpath+"/aspects/no_aspect.json") as f:
        data = json.load(f)

    mapper.context.no_aspect_uid = UID(data[0]['uid']) 
        
    #type_ids = mapper.register.index_content()
    print(mapper.register._index)
    aspects = mapper.register.pretty_search(mapper.register._index, 'name') 
    print(aspects)
    print("Indexed aspects")
    #print(mapper.register._index["Aspect"])
    print("==============================")
    for do in store.info.objects:
        logging.debug("%s %s", do.id, do.type)
    print(args, args.input, mlayerpath)
    
    print(len(mapper.context.scale_reg._objects.keys()))
    for key in mapper.context.scale_reg._objects.keys():
        print(key)
    for key in mapper.context.aspect_reg._objects.keys():
        print(key)
    for key in mapper.context.conversion_reg._table.keys():
        print(key)
    ml_photon_energy_uid = UID(['ml_photon_energy', 291306321925738991196807372973812640971]) 

    ml_si_joule_ratio_uid = UID(['ml_si_joule_ratio', 165050666678496469850612022016789737781])
    ml_electronvolt_ratio_uid = UID(['ml_electronvolt_ratio', 121864523473489992307630707008460819401]) 
    ml_si_THz_ratio_uid = UID(['ml_si_THz_ratio', 271382954339420591832277422907953823861]) 
    ml_si_per_centimetre_ratio_uid = UID(['ml_si_cm-1_ratio', 333995508470114516586033303775415043902]) 
    ml_si_nanometre_ratio_uid = UID(['ml_si_nm_ratio', 257091757625055920788370123828667027186]) 
    ml_energy_uid = UID(["ml_energy",12139911566084412692636353460656684046])
    try:
        ok = mapper.context.convertible(ml_electronvolt_ratio_uid,
                                    ml_photon_energy_uid, 
                                    ml_si_THz_ratio_uid) 
    except RuntimeError as e:
        print(e)

    try:
        ok = mapper.context.convertible(ml_electronvolt_ratio_uid, 
                                    ml_energy_uid,
                                    ml_si_THz_ratio_uid) 
    except RuntimeError as e:
        print(e)
    
    try:
        ok = mapper.context.convertible(ml_si_joule_ratio_uid, 
                                    ml_photon_energy_uid, 
                                    ml_electronvolt_ratio_uid) 
        logging.info("Convertible scale %s", ok)
    except RuntimeError as e:
        print(e)

    try:
        ok = mapper.context.convertible(ml_si_joule_ratio_uid,
                                    ml_energy_uid,
                                    ml_electronvolt_ratio_uid)
        logging.info("Convertible scale %s", ok)
    except RuntimeError as e:
        print(e)
    try:
        ok = mapper.context.convertible(UID(['ml_electronvolt_ratio', 121864523473489992307630707008460819401]),
                UID(["ml_energy",12139911566084412692636353460656684046]),
                UID(['ml_si_joule_ratio', 165050666678496469850612022016789737781]))
        logging.info("Convertible scale %s", ok)
    except RuntimeError as e:
        print(e)
            
    scale_pair = (UID(['ml_electronvolt_ratio', 121864523473489992307630707008460819401]),UID(['ml_si_joule_ratio', 165050666678496469850612022016789737781]))
    cnv = mapper.context.conversion_reg[scale_pair]
    print(cnv)
    if scale_pair in mapper.context.conversion_reg:
        print("Found the pair")
    #print(mapper.context.scale_reg["ml_electronvolt_ratio"])
    #x = expr(1, ml_electronvolt_ratio, ml_photon_energy)
    #t = value(x.convert(ml_si_terahertz_ratio))
    #print(x, t)



# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: mlayerv2.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2
from google.protobuf import any_pb2 as google_dot_protobuf_dot_any__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0emlayerv2.proto\x12\x06mlayer\x1a\x1fgoogle/protobuf/timestamp.proto\x1a\x19google/protobuf/any.proto\"t\n\rDigitalObject\x12\n\n\x02id\x18\x01 \x01(\t\x12\x0c\n\x04type\x18\x02 \x01(\t\x12\"\n\x08metadata\x18\x03 \x01(\x0b\x32\x10.mlayer.Metadata\x12%\n\x07\x63ontent\x18\x04 \x01(\x0b\x32\x14.google.protobuf.Any\"\x93\x01\n\x08Metadata\x12\x11\n\tcreatedOn\x18\x01 \x01(\x03\x12\x11\n\tcreatedBy\x18\x02 \x01(\t\x12\x12\n\nmodifiedOn\x18\x03 \x01(\x03\x12\x12\n\nmodifiedBy\x18\x04 \x01(\t\x12\x11\n\tisVersion\x18\x05 \x01(\x08\x12\x11\n\tversionOf\x18\x06 \x01(\t\x12\x13\n\x0bpublishedBy\x18\x07 \x01(\t\"s\n\x12\x44igitalObjectStore\x12\x1e\n\x02id\x18\x01 \x01(\x0b\x32\x12.mlayer.Identifier\x12\x0f\n\x07\x61\x64\x64ress\x18\x02 \x01(\t\x12,\n\x04info\x18\x03 \x01(\x0b\x32\x1e.mlayer.DigitalObjectStoreInfo\"\x9d\x01\n\x16\x44igitalObjectStoreInfo\x12+\n\x07\x63reated\x18\x01 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12.\n\x03\x61ux\x18\x02 \x01(\x0b\x32!.mlayer.DigitalObjectStoreAuxInfo\x12&\n\x07objects\x18\x03 \x03(\x0b\x32\x15.mlayer.DigitalObject\"0\n\x19\x44igitalObjectStoreAuxInfo\x12\x13\n\x0b\x64\x65scription\x18\x01 \x01(\t\"L\n\nIdentifier\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t\x12\x0c\n\x04type\x18\x03 \x01(\t\x12\x13\n\x0b\x64\x65scription\x18\x04 \x01(\t\"7\n\x07\x43ontext\x12\x0e\n\x06locale\x18\x01 \x01(\t\x12\x0c\n\x04name\x18\x02 \x01(\t\x12\x0e\n\x06symbol\x18\x03 \x01(\t\"\xe9\x01\n\x06\x41spect\x12\x1e\n\x02id\x18\x01 \x01(\x0b\x32\x12.mlayer.Identifier\x12 \n\x07\x63ontext\x18\x02 \x03(\x0b\x32\x0f.mlayer.Context\x12\x12\n\ndefinition\x18\x03 \x01(\t\x12(\n\x0c\x61lternate_id\x18\x04 \x03(\x0b\x32\x12.mlayer.Identifier\x12.\n\x08metadata\x18\x05 \x03(\x0b\x32\x1c.mlayer.Aspect.MetadataEntry\x1a/\n\rMetadataEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t:\x02\x38\x01\"\x99\x01\n\x05Scale\x12\x1e\n\x02id\x18\x01 \x01(\x0b\x32\x12.mlayer.Identifier\x12 \n\x07\x63ontext\x18\x02 \x01(\x0b\x32\x0f.mlayer.Context\x12$\n\tscaletype\x18\x05 \x01(\x0e\x32\x11.mlayer.ScaleType\x12(\n\x0creference_id\x18\x06 \x01(\x0b\x32\x12.mlayer.Identifier\"L\n\x06System\x12\x1e\n\x02id\x18\x01 \x01(\x0b\x32\x12.mlayer.Identifier\x12\x12\n\ndimensions\x18\x02 \x03(\x05\x12\x0e\n\x06prefix\x18\x03 \x01(\x01\"\xab\x01\n\tReference\x12\x1e\n\x02id\x18\x01 \x01(\x0b\x32\x12.mlayer.Identifier\x12 \n\x07\x63ontext\x18\x02 \x03(\x0b\x32\x0f.mlayer.Context\x12\x12\n\ndefinition\x18\x03 \x01(\t\x12\x1e\n\x06system\x18\x04 \x03(\x0b\x32\x0e.mlayer.System\x12(\n\x0c\x61lternate_id\x18\x05 \x03(\x0b\x32\x12.mlayer.Identifier\"]\n\nUnitSystem\x12\x1e\n\x02id\x18\x01 \x01(\x0b\x32\x12.mlayer.Identifier\x12\x0c\n\x04name\x18\x02 \x01(\t\x12!\n\x05\x62\x61sis\x18\x03 \x03(\x0b\x32\x12.mlayer.Identifier\"\xab\x01\n\nConversion\x12\x1e\n\x02id\x18\x01 \x01(\x0b\x32\x12.mlayer.Identifier\x12\"\n\x06src_id\x18\x02 \x01(\x0b\x32\x12.mlayer.Identifier\x12\"\n\x06\x64st_id\x18\x03 \x01(\x0b\x32\x12.mlayer.Identifier\x12$\n\tscaletype\x18\x04 \x01(\x0e\x32\x11.mlayer.ScaleType\x12\x0f\n\x07\x66\x61\x63tors\x18\x05 \x03(\t\"\xb1\x01\n\x0fScalesForAspect\x12\x1e\n\x02id\x18\x01 \x01(\x0b\x32\x12.mlayer.Identifier\x12%\n\taspect_id\x18\x02 \x01(\x0b\x32\x12.mlayer.Identifier\x12\"\n\x06src_id\x18\x03 \x01(\x0b\x32\x12.mlayer.Identifier\x12\"\n\x06\x64st_id\x18\x04 \x01(\x0b\x32\x12.mlayer.Identifier\x12\x0f\n\x07\x66\x61\x63tors\x18\x06 \x03(\t\"z\n\x0b\x41spectScale\x12\x1e\n\x02id\x18\x01 \x01(\x0b\x32\x12.mlayer.Identifier\x12%\n\taspect_id\x18\x02 \x01(\x0b\x32\x12.mlayer.Identifier\x12$\n\x08scale_id\x18\x03 \x01(\x0b\x32\x12.mlayer.Identifier\"\x8f\x03\n\x04\x43\x61st\x12\x1e\n\x02id\x18\x01 \x01(\x0b\x32\x12.mlayer.Identifier\x12\"\n\x06src_id\x18\x02 \x01(\x0b\x32\x12.mlayer.Identifier\x12)\n\rsrc_aspect_id\x18\x03 \x01(\x0b\x32\x12.mlayer.Identifier\x12(\n\x0csrc_scale_id\x18\x04 \x01(\x0b\x32\x12.mlayer.Identifier\x12\"\n\x06\x64st_id\x18\x05 \x01(\x0b\x32\x12.mlayer.Identifier\x12)\n\rdst_aspect_id\x18\x06 \x01(\x0b\x32\x12.mlayer.Identifier\x12(\n\x0c\x64st_scale_id\x18\x07 \x01(\x0b\x32\x12.mlayer.Identifier\x12\x10\n\x08\x66unction\x18\x08 \x01(\t\x12\x30\n\nparameters\x18\t \x03(\x0b\x32\x1c.mlayer.Cast.ParametersEntry\x1a\x31\n\x0fParametersEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t:\x02\x38\x01*H\n\tScaleType\x12\x08\n\x04NONE\x10\x00\x12\t\n\x05RATIO\x10\x01\x12\x0c\n\x08INTERVAL\x10\x02\x12\x0b\n\x07ORDINAL\x10\x03\x12\x0b\n\x07\x42OUNDED\x10\x04\x62\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'mlayerv2_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _ASPECT_METADATAENTRY._options = None
  _ASPECT_METADATAENTRY._serialized_options = b'8\001'
  _CAST_PARAMETERSENTRY._options = None
  _CAST_PARAMETERSENTRY._serialized_options = b'8\001'
  _SCALETYPE._serialized_start=2435
  _SCALETYPE._serialized_end=2507
  _DIGITALOBJECT._serialized_start=86
  _DIGITALOBJECT._serialized_end=202
  _METADATA._serialized_start=205
  _METADATA._serialized_end=352
  _DIGITALOBJECTSTORE._serialized_start=354
  _DIGITALOBJECTSTORE._serialized_end=469
  _DIGITALOBJECTSTOREINFO._serialized_start=472
  _DIGITALOBJECTSTOREINFO._serialized_end=629
  _DIGITALOBJECTSTOREAUXINFO._serialized_start=631
  _DIGITALOBJECTSTOREAUXINFO._serialized_end=679
  _IDENTIFIER._serialized_start=681
  _IDENTIFIER._serialized_end=757
  _CONTEXT._serialized_start=759
  _CONTEXT._serialized_end=814
  _ASPECT._serialized_start=817
  _ASPECT._serialized_end=1050
  _ASPECT_METADATAENTRY._serialized_start=1003
  _ASPECT_METADATAENTRY._serialized_end=1050
  _SCALE._serialized_start=1053
  _SCALE._serialized_end=1206
  _SYSTEM._serialized_start=1208
  _SYSTEM._serialized_end=1284
  _REFERENCE._serialized_start=1287
  _REFERENCE._serialized_end=1458
  _UNITSYSTEM._serialized_start=1460
  _UNITSYSTEM._serialized_end=1553
  _CONVERSION._serialized_start=1556
  _CONVERSION._serialized_end=1727
  _SCALESFORASPECT._serialized_start=1730
  _SCALESFORASPECT._serialized_end=1907
  _ASPECTSCALE._serialized_start=1909
  _ASPECTSCALE._serialized_end=2031
  _CAST._serialized_start=2034
  _CAST._serialized_end=2433
  _CAST_PARAMETERSENTRY._serialized_start=2384
  _CAST_PARAMETERSENTRY._serialized_end=2433
# @@protoc_insertion_point(module_scope)

# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: raft.proto
# Protobuf Python Version: 4.25.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\nraft.proto\x12\x04raft\"\"\n\x0fServeClientArgs\x12\x0f\n\x07Request\x18\x01 \x01(\t\"C\n\x10ServeClientReply\x12\x0c\n\x04\x44\x61ta\x18\x01 \x01(\t\x12\x10\n\x08LeaderID\x18\x02 \x01(\t\x12\x0f\n\x07Success\x18\x03 \x01(\x08\"\x85\x01\n\x11\x41ppendEntriesArgs\x12\x0c\n\x04Term\x18\x01 \x01(\t\x12\x10\n\x08LeaderID\x18\x02 \x01(\t\x12\x14\n\x0cPrevLogIndex\x18\x03 \x01(\t\x12\x13\n\x0bPrevLogTerm\x18\x04 \x01(\t\x12\x0f\n\x07\x45ntries\x18\x05 \x03(\t\x12\x14\n\x0cLeaderCommit\x18\x06 \x01(\t\"3\n\x12\x41ppendEntriesReply\x12\x0c\n\x04Term\x18\x01 \x01(\t\x12\x0f\n\x07Success\x18\x02 \x01(\x08\"_\n\x0fRequestVoteArgs\x12\x0c\n\x04Term\x18\x01 \x01(\t\x12\x13\n\x0b\x43\x61ndidateID\x18\x02 \x01(\t\x12\x14\n\x0cLastLogIndex\x18\x03 \x01(\t\x12\x13\n\x0bLastLogTerm\x18\x04 \x01(\t\"8\n\x13RequestVoteResponse\x12\x0c\n\x04Term\x18\x01 \x01(\t\x12\x13\n\x0bVoteGranted\x18\x02 \x01(\x08\x32\xcd\x01\n\x08Services\x12<\n\x0bServeClient\x12\x15.raft.ServeClientArgs\x1a\x16.raft.ServeClientReply\x12\x42\n\rAppendEntries\x12\x17.raft.AppendEntriesArgs\x1a\x18.raft.AppendEntriesReply\x12?\n\x0bRequestVote\x12\x15.raft.RequestVoteArgs\x1a\x19.raft.RequestVoteResponseb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'raft_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  DESCRIPTOR._options = None
  _globals['_SERVECLIENTARGS']._serialized_start=20
  _globals['_SERVECLIENTARGS']._serialized_end=54
  _globals['_SERVECLIENTREPLY']._serialized_start=56
  _globals['_SERVECLIENTREPLY']._serialized_end=123
  _globals['_APPENDENTRIESARGS']._serialized_start=126
  _globals['_APPENDENTRIESARGS']._serialized_end=259
  _globals['_APPENDENTRIESREPLY']._serialized_start=261
  _globals['_APPENDENTRIESREPLY']._serialized_end=312
  _globals['_REQUESTVOTEARGS']._serialized_start=314
  _globals['_REQUESTVOTEARGS']._serialized_end=409
  _globals['_REQUESTVOTERESPONSE']._serialized_start=411
  _globals['_REQUESTVOTERESPONSE']._serialized_end=467
  _globals['_SERVICES']._serialized_start=470
  _globals['_SERVICES']._serialized_end=675
# @@protoc_insertion_point(module_scope)

# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import raft_pb2 as raft__pb2


class ServicesStub(object):
    """define services
    """

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.ServeClient = channel.unary_unary(
                '/raft.Services/ServeClient',
                request_serializer=raft__pb2.ServeClientArgs.SerializeToString,
                response_deserializer=raft__pb2.ServeClientReply.FromString,
                )
        self.RequestVote = channel.unary_unary(
                '/raft.Services/RequestVote',
                request_serializer=raft__pb2.RequestVoteArgs.SerializeToString,
                response_deserializer=raft__pb2.RequestVoteResponse.FromString,
                )
        self.ReplicateLogRequest = channel.unary_unary(
                '/raft.Services/ReplicateLogRequest',
                request_serializer=raft__pb2.ReplicateLogArgs.SerializeToString,
                response_deserializer=raft__pb2.ReplicateLogResponse.FromString,
                )


class ServicesServicer(object):
    """define services
    """

    def ServeClient(self, request, context):
        """client -> requests certain data from the server
        server -> replies w/ data, leader id, bool variable depicting success or failure

        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def RequestVote(self, request, context):
        """invoked by node when in candidate set to request for votes
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ReplicateLogRequest(self, request, context):
        """invoked by leader node to replicate log
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_ServicesServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'ServeClient': grpc.unary_unary_rpc_method_handler(
                    servicer.ServeClient,
                    request_deserializer=raft__pb2.ServeClientArgs.FromString,
                    response_serializer=raft__pb2.ServeClientReply.SerializeToString,
            ),
            'RequestVote': grpc.unary_unary_rpc_method_handler(
                    servicer.RequestVote,
                    request_deserializer=raft__pb2.RequestVoteArgs.FromString,
                    response_serializer=raft__pb2.RequestVoteResponse.SerializeToString,
            ),
            'ReplicateLogRequest': grpc.unary_unary_rpc_method_handler(
                    servicer.ReplicateLogRequest,
                    request_deserializer=raft__pb2.ReplicateLogArgs.FromString,
                    response_serializer=raft__pb2.ReplicateLogResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'raft.Services', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class Services(object):
    """define services
    """

    @staticmethod
    def ServeClient(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/raft.Services/ServeClient',
            raft__pb2.ServeClientArgs.SerializeToString,
            raft__pb2.ServeClientReply.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def RequestVote(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/raft.Services/RequestVote',
            raft__pb2.RequestVoteArgs.SerializeToString,
            raft__pb2.RequestVoteResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def ReplicateLogRequest(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/raft.Services/ReplicateLogRequest',
            raft__pb2.ReplicateLogArgs.SerializeToString,
            raft__pb2.ReplicateLogResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

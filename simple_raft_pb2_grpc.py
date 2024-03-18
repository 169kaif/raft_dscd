# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import simple_raft_pb2 as simple__raft__pb2


class RaftStub(object):
    """The Raft service definition.
    """

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Heartbeat = channel.unary_unary(
                '/simple_raft.Raft/Heartbeat',
                request_serializer=simple__raft__pb2.HeartbeatRequest.SerializeToString,
                response_deserializer=simple__raft__pb2.HeartbeatResponse.FromString,
                )
        self.SubmitCommand = channel.unary_unary(
                '/simple_raft.Raft/SubmitCommand',
                request_serializer=simple__raft__pb2.CommandRequest.SerializeToString,
                response_deserializer=simple__raft__pb2.CommandResponse.FromString,
                )


class RaftServicer(object):
    """The Raft service definition.
    """

    def Heartbeat(self, request, context):
        """Heartbeat RPC for nodes to interact with each other
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SubmitCommand(self, request, context):
        """Command RPC for clients to interact with nodes
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_RaftServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Heartbeat': grpc.unary_unary_rpc_method_handler(
                    servicer.Heartbeat,
                    request_deserializer=simple__raft__pb2.HeartbeatRequest.FromString,
                    response_serializer=simple__raft__pb2.HeartbeatResponse.SerializeToString,
            ),
            'SubmitCommand': grpc.unary_unary_rpc_method_handler(
                    servicer.SubmitCommand,
                    request_deserializer=simple__raft__pb2.CommandRequest.FromString,
                    response_serializer=simple__raft__pb2.CommandResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'simple_raft.Raft', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class Raft(object):
    """The Raft service definition.
    """

    @staticmethod
    def Heartbeat(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/simple_raft.Raft/Heartbeat',
            simple__raft__pb2.HeartbeatRequest.SerializeToString,
            simple__raft__pb2.HeartbeatResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def SubmitCommand(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/simple_raft.Raft/SubmitCommand',
            simple__raft__pb2.CommandRequest.SerializeToString,
            simple__raft__pb2.CommandResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

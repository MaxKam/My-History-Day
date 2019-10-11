import grpc

import sys
sys.path.append("./rpc_classes")
sys.path.append("../protos")
sys.path.append("./protos")
import get_events_pb2
import get_events_pb2_grpc

class GetEvents(object):

    def __init__(self, rpc_server):
        self.RPC_SERVER = rpc_server

    def get_gcal_events(self, credentials_dict, api_service_name, api_version, requested_date):
        with grpc.insecure_channel('%s:50051' % self.RPC_SERVER) as channel:
            stub = get_events_pb2_grpc.GCalendarEventsStub(channel)
            
            events_request = stub.GetEvents(get_events_pb2.EventsRequest(token=credentials_dict['token'],
            refresh_token=credentials_dict['refresh_token'],
            token_uri=credentials_dict['token_uri'],
            client_id=credentials_dict['client_id'],
            client_secret=credentials_dict['client_secret'],
            scopes=credentials_dict['scopes'],
            api_service_name=api_service_name,
            api_version=api_version,
            requested_date=requested_date
            ))
            
            events_list = {}
            for event in events_request:
                if event.event_title == "No events":
                    return "No events"
                else:
                    events_list[event.event_start_time] = event.event_title
            return events_list
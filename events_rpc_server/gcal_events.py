import sys
sys.path.append("../protos")

import datetime
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery

import grpc
import time
import json
import get_events_pb2
import get_events_pb2_grpc
from concurrent import futures

_ONE_DAY_IN_SECONDS = 60 * 60 * 24

def credentials_to_dict(credentials):
  return {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes}


def get_gcal_events(years_back, credentials_dict, api_service_name, api_version, chosen_date):
        # Load credentials from the session.
        credentials = google.oauth2.credentials.Credentials(**credentials_dict)

        service = googleapiclient.discovery.build(
            api_service_name, api_version, credentials=credentials)

        now = datetime.datetime.strptime(chosen_date, '%m/%d/%Y')
        selected_year = now.year
        events_list = {}

        for year in range(selected_year - 1, selected_year - years_back, -1):
            min_time = "%s-%s-%sT00:00:01Z" % (year, now.month, now.day)
            max_time = "%s-%s-%sT23:59:59Z" % (year, now.month, now.day)

            eventsResult = service.events().list(
            calendarId='primary', timeMin=min_time, 
            timeMax=max_time, singleEvents=True,
            orderBy='startTime').execute()
            events = eventsResult.get('items', [])

            if not events:
                continue
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                events_list[start] = event['summary']
        
        if len(events_list) == 0:
            return "No events"

        return events_list


class GetEvents(get_events_pb2_grpc.GCalendarEventsServicer):

    def __init__(self):
        self.years_back = 5

    def GetEvents(self, request, context):
        credentials_dict = credentials_to_dict(request)
        events_list = get_gcal_events(self.years_back,
                    credentials_dict, request.api_service_name, 
                    request.api_version, request.requested_date)
        if events_list == "No events":
            yield get_events_pb2.Event(event_start_time="0", event_title="No events")
        else:
            for event in events_list:
                yield get_events_pb2.Event(event_start_time=event,  
                event_title=events_list[event])
        

    
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    get_events_pb2_grpc.add_GCalendarEventsServicer_to_server(GetEvents(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    serve()
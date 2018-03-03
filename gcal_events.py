import datetime
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery

class GCalEvents(object):

    def __init__(self):
        self.years_back = 5

    def get_gcal_events(self, credentials_dict, api_service_name, api_version, chosen_date):
        # Load credentials from the session.
        credentials = google.oauth2.credentials.Credentials(**credentials_dict)

        service = googleapiclient.discovery.build(
            api_service_name, api_version, credentials=credentials)

        now = datetime.datetime.strptime(chosen_date, '%m/%d/%Y')
        selected_year = now.year
        events_list = {}

        for year in range(selected_year - 1, selected_year - self.years_back, -1):
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

        return events_list
        
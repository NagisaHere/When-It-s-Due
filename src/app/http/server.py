# take in course code
# check if it is a valid course
# allow selection from ecp
# sign into google calendar
# insert into tasks


import datetime
import os.path
from ecp_parse import ecpparser

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from flask import Flask

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/tasks"]


def main():
  """Shows basic usage of the Google Calendar API.
  Prints the start and name of the next 10 events on the user's calendar.
  """
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      # will need ot run this somehow?
      # may need to run a credentials server?
      creds = flow.run_local_server(port=0)
    # # Save the credentials for the next run
    # with open("token.json", "w") as token:
    #   token.write(creds.to_json())


    # GET request to get;
    # course code
    # task list name
    try:
        service = build("tasks", "v1", credentials=creds)
        # Call the Tasks API
        
        # will need to do server

        task_dues = ecpparser()
        if task_dues is None:
           return

        tlist_name = input("\nGive your task list a name: ")

        tasklist_body = {
           'title': tlist_name
        }
        new_list = service.tasklists().insert(body=tasklist_body).execute()

        print("\nPlease wait...")

        for item in task_dues:
           task = {
              'title': item[0],
              'due': item[1].isoformat('T'),
              'notes': "Due at " + item[2]
           }
           service.tasks().insert(body=task, tasklist=new_list['id']).execute()
        
        print("\nDone!")


    except HttpError as error:
        print(f"An error occurred: {error}")


if __name__ == "__main__":
    main()

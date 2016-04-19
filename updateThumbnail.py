#!/usr/bin/python

import httplib
import httplib2
import os
import random
import sys
import time

from apiclient.discovery import build
from apiclient.errors import HttpError
from apiclient.http import MediaFileUpload
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow
from youtubeAuthenticate import get_authenticated_service

#Default Variables
THUMBNAIL = "2016 Walker Warren.png"

VALID_PRIVACY_STATUSES = ("public", "private", "unlisted")

def update_thumbnail(youtube, video_id, file):
  youtube.thumbnails().set(
    videoId=video_id,
    media_body=file
  ).execute()

if __name__ == '__main__':
  argparser.add_argument("--vID", help="Video ID of video to edit", required=True)
  argparser.add_argument("--file", help="Thumbnail file to upload", default=THUMBNAIL)
  args = argparser.parse_args()

  youtube = get_authenticated_service(args)
  try:
    update_thumbnail(youtube,args.vID,args.file)
    print "Thumbnail added to video %s" % args.vID
  except HttpError, e:
    print "An HTTP error %d occurred:\n%s" % (e.resp.status, e.content)
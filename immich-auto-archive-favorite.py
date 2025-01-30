#!/usr/bin/env python3

import logging, sys
from itertools import groupby
import json
import os
import re
import time

from requests import Session
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from urllib.parse import urlparse

logging.basicConfig(
  stream=sys.stdout, 
  level=logging.INFO, 
  format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Immich():
  def __init__(self, url: str, key: str):
    self.api_url = f'{urlparse(url).scheme}://{urlparse(url).netloc}/api'
    self.headers = {
      'x-api-key': key,
      'Accept': 'application/json'
    }
    self.assets = list()
    self.stacks = list()
  
  def fetchAssets(self, size: int = 1000) -> list:
    payload = {
      'size' : size,
      'page' : 1,
      'withExif': True,
      #'withStacked': True
    }
    assets_total = list()

    logger.info(f'⬇️  Fetching assets: ')
    logger.info(f'   Page size: {size}')

    session = Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    while payload["page"] != None:
      response = session.post(f"{self.api_url}/search/metadata", headers=self.headers, json=payload)
      if not response.ok:
        logger.error('   Error:', response.status_code, response.text)
      response_data = response.json()

      assets_total = assets_total + response_data['assets']['items']
      payload["page"] = response_data['assets']['nextPage']
    
    self.assets = assets_total
    
    logger.info(f'   Pages: {payload["page"]}')   
    logger.info(f'   Assets: {len(self.assets)}')
    
    return self.assets

  def updateAssets(self, assets: list, dry_run: bool) -> None:
    updateLists = {True: {True:[],False:[]}, False: {False:[],True:[]} }
    for asset in assets:
       isFavorite = (asset['exifInfo']['rating'] == 5)
       isArchived = (asset['exifInfo']['rating'] == -1)
       if(isFavorite != asset['isFavorite'] or isArchived != asset['isArchived']):
          updateLists[isArchived][isFavorite].append(asset["id"])

    for isArchived in updateLists:
      for isFavorite in updateLists[isArchived]:
        if len(updateLists[isArchived][isFavorite]) > 0:
          payload = {
            "ids": updateLists[isArchived][isFavorite],
            "isArchived": isArchived,
            "isFavorite": isFavorite
          }
          logger.info(f'⬆️  Updating {len(updateLists[isArchived][isFavorite])} assets (Favorite: {isFavorite}, Archive: {isArchived}): ')

          if not dry_run:
            session = Session()
            retry = Retry(connect=3, backoff_factor=0.5)
            adapter = HTTPAdapter(max_retries=retry)
            session.mount('http://', adapter)
            session.mount('https://', adapter)

            response = session.put(f"{self.api_url}/assets", headers=self.headers, json=payload)
            if response.ok:
              logger.info("  🟢 Success!")
            else:
              logger.error(f"  🔴 Error! {response.status_code} {response.text}") 
          else: 
            logger.info("  ⏭️  Skipped (dry-run)")
    return

def main():

  api_key = os.environ.get("API_KEY", False)

  api_url = os.environ.get("API_URL", "http://immich_server:3001/api")

  dry_run = os.environ.get("DRY_RUN") == "True"

  if not api_key:
    logger.warn("API key is required")
    return

  logger.info('============== INITIALIZING ==============')

  if dry_run:
    logger.info('🔒  Dry run enabled, no changes will be applied')
  
  immich = Immich(api_url, api_key)
  
  assets = immich.fetchAssets()
  immich.updateAssets(assets,dry_run)
  
if __name__ == '__main__':
  main()

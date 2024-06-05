# -*- coding: utf-8 -*-
import asyncio
import requests
import json
import os
import platform

from src.trackers.COMMON import COMMON
from src.console import console


class R4E():

    def __init__(self, config):
        self.config = config
        self.tracker = 'R4E'
        self.source_flag = 'R4E'
        self.upload_url = 'https://racing4everyone.eu/api/torrents/upload'
        self.search_url = 'https://racing4everyone.eu/api/torrents/filter'
        self.banned_groups = [""]
        pass

    async def get_cat_id(self, category_name, genres):
        if category_name == 'MOVIE':
            if 'documentary' in map(str.strip, genres.lower().split(',')):
                category_id = '66' # Documentary
            else:
                category_id = '70' # Motorsports Movie
        elif category_name == 'TV':
            if 'documentary' in map(str.strip, genres.lower().split(',')):
                category_id = '2' # TV Documentary
            else:
                category_id = '79' # TV Series
        else:
            category_id = '24' 
        return category_id

    async def get_type_id(self, type):
        type_id = {
            '8640p':'2160p', 
            '4320p': '2160p', 
            '2160p': '2160p', 
            '1440p' : '1080p',
            '1080p': '1080p',
            '1080i':'1080i', 
            '720p': '720p',  
            '576p': 'SD', 
            '576i': 'SD',
            '480p': 'SD', 
            '480i': 'SD'
            }.get(type, '10')
        return type_id

    ###############################################################
    ######   STOP HERE UNLESS EXTRA MODIFICATION IS NEEDED   ######
    ###############################################################

    async def upload(self, meta):
        common = COMMON(config=self.config)
        await common.edit_torrent(meta, self.tracker, self.source_flag)
        cat_id = await self.get_cat_id(meta['category'])
        type_id = await self.get_type_id(meta['type'])
        await common.unit3d_edit_desc(meta, self.tracker)
        name = await self.edit_name(meta)
        if meta['anon'] != 0 or self.config['TRACKERS'][self.tracker].get('anon', False):
            anon = 1
        else:
            anon = 0

        if meta['bdinfo'] != None:
            mi_dump = None
            bd_dump = open(f"{meta['base_dir']}/tmp/{meta['uuid']}/BD_SUMMARY_00.txt", 'r', encoding='utf-8').read()
        else:
            mi_dump = open(f"{meta['base_dir']}/tmp/{meta['uuid']}/MEDIAINFO.txt", 'r', encoding='utf-8').read()
            bd_dump = None
        desc = open(f"{meta['base_dir']}/tmp/{meta['uuid']}/[{self.tracker}]DESCRIPTION.txt", 'r').read()
        open_torrent = open(f"{meta['base_dir']}/tmp/{meta['uuid']}/[{self.tracker}]{meta['clean_name']}.torrent", 'rb')
        files = {'torrent': open_torrent}
        data = {
            'name' : name,
            'description' : desc,
            'mediainfo' : mi_dump,
            'bdinfo' : bd_dump, 
            'category_id' : cat_id,
            'type_id' : type_id,
            'tmdb' : meta['tmdb'],
            'imdb' : meta['imdb_id'].replace('tt', ''),
            'tvdb' : meta['tvdb_id'],
            'mal' : meta['mal_id'],
            'igdb' : 0,
            'anonymous' : anon,
            'stream' : meta['stream'],
            'sd' : meta['sd'],
            'keywords' : meta['keywords'],
            # 'personal_release' : int(meta.get('personalrelease', False)), # NOT IMPLEMENTED on R4E
            # 'internal' : 0,
            # 'featured' : 0,
            # 'free' : 0,
            # 'doubleup' : 0,
            # 'sticky' : 0,
        }
        # Internal
        # if self.config['TRACKERS'][self.tracker].get('internal', False):
        #     if meta['tag'] != "" and (meta['tag'][1:] in self.config['TRACKERS'][self.tracker].get('internal_groups', [])):
        #         data['internal'] = 1
                
        if meta.get('category') == "TV":
            data['season_number'] = meta.get('season_int', '0')
            data['episode_number'] = meta.get('episode_int', '0')
        headers = {
            'User-Agent': f'Uploadrr ({platform.system()} {platform.release()})'
        }
        params = {
            'api_token' : self.config['TRACKERS'][self.tracker]['api_key'].strip()
        }
        
        if not meta['debug']:
            success = False
            data = {}
            try:
                response = requests.post(url=self.upload_url, files=files, data=data, headers=headers, params=params)
                response.raise_for_status()                
                response_json = response.json()
                success = response_json.get('success', False)
                data = response_json.get('data', {})
            except Exception as e:
                console.print(f"[red]Encountered Error: {e}[/red]\n[bold yellow]May have uploaded, please go check..")
            if success:
                console.print("[bold green]Torrent uploaded successfully!")
            else:
                console.print("[bold red]Torrent upload failed.")

            if 'name' in data and 'The name has already been taken.' in data['name']:
                console.print("[red]Name has already been taken.")
            if 'info_hash' in data and 'The info hash has already been taken.' in data['info_hash']:
                console.print("[red]Info hash has already been taken.")
            return success
        
        else:
            console.print("[cyan]Request Data:")
            console.print(data)
        open_torrent.close()

    async def edit_name(self, meta):
        name = meta['name']
        return name

    async def search_existing(self, meta):
        dupes = {}
        console.print("[yellow]Searching for existing torrents on site...")
        params = {
            'api_token' : self.config['TRACKERS'][self.tracker]['api_key'].strip(),
            'tmdbId' : meta['tmdb'],
            'categories[]' : await self.get_cat_id(meta['category']),
            'types[]' : await self.get_type_id(meta['type']),
            'name' : ""
        }
        if meta['category'] == 'TV':
            params['name'] = f"{meta.get('season', '')}{meta.get('episode', '')}"
        if meta.get('edition', "") != "":
            params['name'] = params['name'] + meta['edition']
        try:
            response = requests.get(url=self.search_url, params=params)
            response = response.json()
            for each in response['data']:
                result = each['attributes']['name']
                size = each['attributes']['size']
                dupes[result] = size
        except Exception:
            console.print('[bold red]Unable to search for existing torrents on site. Either the site is down or your API key is incorrect')
            await asyncio.sleep(5)

        return dupes

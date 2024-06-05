# -*- coding: utf-8 -*-
# import discord
import os
import asyncio
import requests
import json
import platform
from pymediainfo import MediaInfo

from src.trackers.COMMON import COMMON
from src.console import console


class ANT():

    def __init__(self, config):
        self.config = config
        self.tracker = 'ANT'
        self.source_flag = 'ANT'
        self.search_url = 'https://anthelion.me/api.php'
        self.upload_url = 'https://anthelion.me/api.php'
        self.banned_groups = ['Ozlem', 'RARBG', 'FGT', 'STUTTERSHIT', 'LiGaS', 'DDR', 'Zeus', 'TBS', 'aXXo', 'CrEwSaDe', 'DNL', 'EVO',
                              'FaNGDiNG0', 'HD2DVD', 'HDTime', 'iPlanet', 'KiNGDOM', 'NhaNc3', 'PRoDJi', 'SANTi', 'ViSiON', 'WAF', 'YIFY',
                              'YTS', 'MkvCage', 'mSD']
        pass

    async def get_flags(self, meta):
        flags = []
        for each in ['Directors', 'Extended', 'Uncut', 'Unrated', '4KRemaster']:
            if each in meta['edition'].replace("'", ""):
                flags.append(each)
        for each in ['Dual-Audio', 'Atmos']:
            if each in meta['audio']:
                flags.append(each.replace('-', ''))
        if meta.get('has_commentary', False):
            flags.append('Commentary')
        if meta['3D'] == "3D":
            flags.append('3D')
        if "HDR" in meta['hdr']:
            flags.append('HDR10')
        if "DV" in meta['hdr']:
            flags.append('DV')
        if "Criterion" in meta.get('distributor', ''):
            flags.append('Criterion')
        if "REMUX" in meta['type']:
            flags.append('Remux')
        return flags

    ###############################################################
    # ####   STOP HERE UNLESS EXTRA MODIFICATION IS NEEDED    ### #
    ###############################################################

    async def upload(self, meta):
        common = COMMON(config=self.config)
        await common.edit_torrent(meta, self.tracker, self.source_flag)
        flags = await self.get_flags(meta)
        if meta['anon'] != 0 or self.config['TRACKERS'][self.tracker].get('anon', False):
            anon = 1
        else:
            anon = 0

        if meta['bdinfo'] is not None:
            bd_dump = open(f"{meta['base_dir']}/tmp/{meta['uuid']}/BD_SUMMARY_00.txt", 'r', encoding='utf-8').read()
            bd_dump = f'[spoiler=BDInfo][pre]{bd_dump}[/pre][/spoiler]'
            path = os.path.join(meta['bdinfo']['path'], 'STREAM')
            m2ts = os.path.join(path, meta['bdinfo']['files'][0]['file'])
            media_info_output = str(MediaInfo.parse(m2ts, output="text", full=False))
            mi_dump = media_info_output.replace('\r\n', '\n')
        else:
            mi_dump = open(f"{meta['base_dir']}/tmp/{meta['uuid']}/MEDIAINFO.txt", 'r', encoding='utf-8').read()
        open_torrent = open(f"{meta['base_dir']}/tmp/{meta['uuid']}/[{self.tracker}]{meta['clean_name']}.torrent", 'rb')
        files = {'file_input': open_torrent}
        data = {
            'api_key': self.config['TRACKERS'][self.tracker]['api_key'].strip(),
            'action': 'upload',
            'tmdbid': meta['tmdb'],
            'mediainfo': mi_dump,
            'flags[]': flags,
            'anonymous': anon,
            'screenshots': '\n'.join([x['raw_url'] for x in meta['image_list']][:4])
        }
        if meta['bdinfo'] is not None:
            data.update({
                'media': 'Blu-ray',
                'releasegroup': str(meta['tag'])[1:],
                'release_desc': bd_dump,
                'flagchangereason': "BDMV Uploaded with L4G's Upload Assistant"})
        if meta['scene']:
            # ID of "Scene?" checkbox on upload form is actually "censored"
            data['censored'] = 1
        headers = {
            'User-Agent': f'Uploadrr ({platform.system()} {platform.release()})'
        }
        if not meta['debug']:
            success = False
            data = {}
            try:
                response = requests.post(url=self.upload_url, files=files, data=data, headers=headers)
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

    async def edit_desc(self, meta):
        return


    async def search_existing(self, meta):
        dupes = {}
        console.print("[yellow]Searching for existing torrents on site...")
        params = {
            'apikey': self.config['TRACKERS'][self.tracker]['api_key'].strip(),
            't': 'search',
            'o': 'json'
        }
        if str(meta['tmdb']) != "0":
            params['tmdb'] = meta['tmdb']
        elif int(meta['imdb_id'].replace('tt', '')) != 0:
            params['imdb'] = meta['imdb_id']
        try:
            response = requests.get(url='https://anthelion.me/api', params=params)
            response = response.json()
            for each in response['item']:
                largest = each['files'][0]
                for file in each['files']:
                    if int(file['size']) > int(largest['size']):
                        largest = file
                result = largest['name']
                size = largest['size']
                dupes[result] = size
        ## CvT: I have no access to ANT and don't know why their sorting dupes by size. I merely adapted the code to produce the dictionary needed for printout, as well as size comparing.        
        except Exception as e:
            console.print(f'[bold red]Unable to search for existing torrents on site. Either the site is down or your API key is incorrect. Error: {e}')
            await asyncio.sleep(5)

        return dupes
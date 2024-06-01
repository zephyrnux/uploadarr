# -*- coding: utf-8 -*-
import asyncio
import requests
import json
from guessit import guessit 

from src.trackers.COMMON import COMMON
from src.console import console


class NBL():

    def __init__(self, config):
        self.config = config
        self.tracker = 'NBL'
        self.source_flag = 'NBL'
        self.upload_url = 'https://nebulance.io/upload.php'
        self.search_url = 'https://nebulance.io/api.php'
        self.api_key = self.config['TRACKERS'][self.tracker]['api_key'].strip()
        self.banned_groups = ['0neshot', '3LTON', '4yEo', '[Oj]', 'AFG', 'AkihitoSubs', 'AniHLS', 'Anime', 'Time', 'AnimeRG', 'AniURL', 'ASW', 'BakedFish', 'bonkai77', 'Cleo', 'DeadFish', 'DeeJayAhmed', 'ELiTE', 'EMBER', 'eSc', 'FGT', 'FUM', 'GERMini', 'HAiKU', 'Hi10', 'ION10', 'JacobSwaggedUp', 'JIVE', 'Judas', 'LOAD', 'MeGusta', 'Mr.Deadpool', 'mSD', 'NemDiggers', 'neoHEVC', 'NhaNc3', 'NOIVTC', 'PlaySD', 'playXD', 'project-gxs', 'PSA', 'QaS', 'Ranger', 'RAPiDCOWS', 'Raze', 'Reaktor', 'REsuRRecTioN', 'RMTeam', 'SpaceFish', 'SPASM', 'SSA', 'Telly', 'Tenrai-Sensei', 'TM', 'Trix', 'URANiME', 'VipapkStudios', 'ViSiON', 'Wardevil', 'xRed', 'XS', 'YakuboEncodes', 'YuiSubs', 'ZKBL', 'ZmN', 'ZMNT']
        pass
    

    async def get_cat_id(self, meta):
        if meta.get('tv_pack', 0) == 1:
            cat_id = 3
        else:
            cat_id = 1
        return cat_id

    ###############################################################
    ######   STOP HERE UNLESS EXTRA MODIFICATION IS NEEDED   ######
    ###############################################################
    async def edit_desc(self, meta):
        # Leave this in so manual works
        return

    async def upload(self, meta):
        if meta['category'] != 'TV':
            console.print("[red]Only TV Is allowed at NBL")
            return
        common = COMMON(config=self.config)
        await common.edit_torrent(meta, self.tracker, self.source_flag)

        if meta['bdinfo'] != None:
            mi_dump = open(f"{meta['base_dir']}/tmp/{meta['uuid']}/BD_SUMMARY_00.txt", 'r', encoding='utf-8').read()
        else:
            mi_dump = open(f"{meta['base_dir']}/tmp/{meta['uuid']}/MEDIAINFO.txt", 'r', encoding='utf-8').read()[:-65].strip()
        open_torrent = open(f"{meta['base_dir']}/tmp/{meta['uuid']}/[{self.tracker}]{meta['clean_name']}.torrent", 'rb')
        files = {'file_input': open_torrent}
        data = {
            'api_key' : self.api_key,
            'tvmazeid' : int(meta.get('tvmaze_id', 0)),
            'mediainfo' : mi_dump,
            'category' : await self.get_cat_id(meta),
            'ignoredupes' : 'on'
        }

        if meta['debug'] == False:
            try:
                response = requests.post(url=self.upload_url, files=files, data=data)
                response.raise_for_status()                
                response_json = response.json()
                success = response_json.get('success', False)
                data = response_json.get('data', {})
            except Exception as e:
                console.print(f"[red]Encountered Error: {e}[/red]\n[bold yellow]May have uploaded, please go check..")
            if success:
                console.print(f"[bold green]Torrent uploaded successfully!")
            else:
                console.print(f"[bold red]Torrent upload failed.")

            if 'name' in data and 'The name has already been taken.' in data['name']:
                console.print(f"[red]Name has already been taken.")
            if 'info_hash' in data and 'The info hash has already been taken.' in data['info_hash']:
                console.print(f"[red]Info hash has already been taken.")
            return success
        
        else:
            console.print(f"[cyan]Request Data:")
            console.print(data)
        open_torrent.close()



    async def search_existing(self, meta):
        dupes = {}
        console.print("[yellow]Searching for existing torrents on site...")
        if int(meta.get('tvmaze_id', 0)) != 0:
            search_term = {'tvmaze' : int(meta['tvmaze_id'])}
        elif int(meta.get('imdb_id', '0').replace('tt', '')) == 0:
            search_term = {'imdb' : meta.get('imdb_id', '0').replace('tt', '')}
        else:
            search_term = {'series' : meta['title']}
        json = {
            'jsonrpc' : '2.0',
            'id' : 1,
            'method' : 'getTorrents',
            'params' : [
                self.api_key, 
                search_term
            ]
        }
        try:
            response = requests.get(url=self.search_url, json=json)
            response = response.json()
            for each in response['result']['items']:
                if meta['resolution'] in each['tags']:
                    if meta.get('tv_pack', 0) == 1:
                        if each['cat'] == "Season" and int(guessit(each['rls_name']).get('season', '1')) == int(meta.get('season_int')):
                            result = each['rls_name']
                            try:
                                size = each ['rls_size']
                            except Exception:
                                size = 0
                            dupes[result] = size      
                    elif int(guessit(each['rls_name']).get('episode', '0')) == int(meta.get('episode_int')):
                            result = each['rls_name']
                            try:
                                size = each ['rls_size']
                            except Exception:
                                size = 0
                            dupes[result] = size 
        except requests.exceptions.JSONDecodeError:
            console.print('[bold red]Unable to search for existing torrents on site. Either the site is down or your API key is incorrect')
            await asyncio.sleep(5)
        except KeyError as e:
            console.print(response)
            console.print("\n\n\n")
            if e.args[0] == 'result':
                console.print(f"Search Term: {search_term}")
                console.print('[red]NBL API Returned an unexpected response, please manually check for dupes')
                result = "ERROR: PLEASE CHECK FOR EXISTING RELEASES MANUALLY"
                size = 0
                dupes[result] = size 
                await asyncio.sleep(5)
            else:
                console.print_exception()
        except Exception:
            console.print_exception()

        return dupes

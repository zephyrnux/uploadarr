# -*- coding: utf-8 -*-
# import discord
import asyncio
import requests
from difflib import SequenceMatcher
import os
import re
import langcodes
import platform
from datetime import datetime

from src.trackers.COMMON import COMMON
from src.console import console


class LDU():

    def __init__(self, config):
        self.config = config
        self.tracker = 'LDU'
        self.source_flag = 'LDU'
        self.upload_url = 'https://theldu.to/api/torrents/upload'
        self.search_url = 'https://theldu.to/api/torrents/filter'
        self.signature = None
        self.banned_groups = ['']
        pass
    
    async def get_cat_id(self, category_name, genres, keywords, service, edition, meta):
        adult = meta.get('adult', False)
        soundmix = meta.get('imdb_info', {}).get('soundmix', [])
        is_silent = 'silent' in soundmix if soundmix else False
        release_date = meta.get('full_date', '')
        if isinstance(release_date, str):
            try:
                release_date = datetime.strptime(release_date, '%Y-%m-%d')
            except ValueError:
                year = meta.get('year')
                if year is not None:
                    release_date = datetime.strptime(f'{year}-01-01', '%Y-%m-%d') 
        year = meta.get('year','')
        tag = self.get_language_tag(meta)
        if tag:
            tags = tag.split(']')
            tags = [t[1:] for t in tags if t]
        category_id = {
            'MOVIE': '1', 
            'TV': '2', 
            'Anime' : '8',
            'FANRES' : '12',
            }.get(category_name, '0') 
        if category_name == 'MOVIE':
            if adult and ('hentai' in map(str.strip, keywords.lower().split(',')) or 'animation' in map(str.strip, keywords.lower().split(','))):
                category_id = '10'
            elif adult is True:
                category_id = '6'
            elif '???' in tags[0]:
                category_id = '27'
            elif tag and 'ENG' not in ''.join(tags):
                category_id = '22'
            elif '3D' in edition:
                category_id = '21'
            elif 'FANRES' in edition.upper() or 'FANEDIT' in edition.upper() or 'RESTORATION' in edition.upper():
                category_id = '12'
            elif release_date != '' and release_date < datetime(1927, 10, 1):
                category_id = '18'
            elif year != '' and year <= 1926:
                category_id = '18'     
            elif 'silent film' in map(str.strip, keywords.lower().split(',')):
                category_id = '18'
            elif is_silent:
                category_id = '18'          
            elif 'holiday' in map(str.strip, keywords.lower().split(',')):
                category_id = '24'     
            elif 'musical' in map(str.strip, keywords.lower().split(',')):
                category_id = '25'                
            elif 'documentary' in map(str.strip, genres.lower().split(',')):
                category_id = '17'
            elif 'stand-up' in map(str.strip, keywords.lower().split(',')):
                category_id = '20'
            elif 'short film' in map(str.strip, keywords.lower().split(',')):
                category_id = '19'                 
            else:
                category_id = '1'                                                            
        elif category_name == 'TV':
            if adult and ('hentai' in map(str.strip, keywords.lower().split(',')) or 'animation' in map(str.strip, keywords.lower().split(','))):
                category_id = '10'
            elif adult is True:
                category_id = '6'            
            elif tag and not all(char.isalpha() or char.isspace() for char in tags[0]):
                category_id = '31'
            elif tag and 'ENG' not in ''.join(tags):
                category_id = '29'
            elif category_name == 'TV' and 'anime' in map(str.strip,keywords.lower().split(',')):    
                category_id = '9'
            else:
                category_id = '2'
        return category_id

    async def get_type_id(self, type, edition):
        type_id = {
            'DISC': '1', 
            'REMUX': '2',
            'WEBDL': '4', 
            'WEBRIP': '5', 
            'HDTV': '6',
            'ENCODE': '3',
            'UPSCALE': '27',
            }.get(type, '0')
        if type == 'ENCODE':
            if 'upscale' in edition.lower() or 'ai' in edition.lower():
                type_id = '27' 
            else:
                type_id = '3'    
        return type_id

    async def get_res_id(self, resolution):
        resolution_id = {
            '8640p':'10', 
            '4320p': '1', 
            '2160p': '2', 
            '1440p' : '3',
            '1080p': '3',
            '1080i':'4', 
            '720p': '5',  
            '576p': '6', 
            '576i': '7',
            '480p': '8', 
            '480i': '9'
            }.get(resolution, '10')
        return resolution_id

    ###############################################################
    ######   STOP HERE UNLESS EXTRA MODIFICATION IS NEEDED   ######
    ###############################################################

    async def upload(self, meta):
        common = COMMON(config=self.config)
        await common.edit_torrent(meta, self.tracker, self.source_flag)
        cat_id = await self.get_cat_id(meta['category'], meta.get('genres', ''), meta.get('keywords', ''), meta.get('service', ''), meta.get('edition', ''), meta)
        type_id = await self.get_type_id(meta['type'],meta['edition'])
        resolution_id = await self.get_res_id(meta['resolution'])
        await common.unit3d_edit_desc(meta, self.tracker)
        region_id = await common.unit3d_region_ids(meta.get('region'))
        distributor_id = await common.unit3d_distributor_ids(meta.get('distributor'))
        if meta['anon'] != 0 or self.config['TRACKERS'][self.tracker].get('anon', "False"):
            anon = 1
        else:
            anon = 0

        if meta['bdinfo'] != None:
            mi_dump = None
            bd_dump = open(f"{meta['base_dir']}/tmp/{meta['uuid']}/BD_SUMMARY_00.txt", 'r', encoding='utf-8').read()
        else:
            mi_dump = open(f"{meta['base_dir']}/tmp/{meta['uuid']}/MEDIAINFO.txt", 'r', encoding='utf-8').read()
            bd_dump = None

        desc = open(f"{meta['base_dir']}/tmp/{meta['uuid']}/[{self.tracker}]DESCRIPTION.txt", 'r', encoding='utf-8').read()
        open_torrent = open(f"{meta['base_dir']}/tmp/{meta['uuid']}/[{self.tracker}]{meta['clean_name']}.torrent", 'rb')
        files = {'torrent': open_torrent}
        data = {
            'name' : await self.get_name(meta),
            'description' : desc,
            'mediainfo' : mi_dump,
            'bdinfo' : bd_dump, 
            'category_id' : cat_id,
            'type_id' : type_id,
            'resolution_id' : resolution_id,
            'tmdb' : meta['tmdb'],
            'imdb' : meta['imdb_id'].replace('tt', ''),
            'tvdb' : meta['tvdb_id'],
            'mal' : meta['mal_id'],
            'igdb' : 0,
            'anonymous' : anon,
            'stream' : meta['stream'],
            'sd' : meta['sd'],
            'keywords' : meta['keywords'],
            'personal_release' : int(meta.get('personalrelease', False)),
            'internal' : 0,
            'featured' : 0,
            'free' : 0,
            'doubleup' : 0,
            'sticky' : 0,
        }
        # Internal
        if self.config['TRACKERS'][self.tracker].get('internal', False):
            if meta['tag'] != "" and (meta['tag'][1:] in self.config['TRACKERS'][self.tracker].get('internal_groups', [])):
                data['internal'] = 1
                
        if region_id != 0:
            data['region_id'] = region_id
        if distributor_id != 0:
            data['distributor_id'] = distributor_id
        if meta.get('category') == "TV":
            data['season_number'] = int(meta.get('season_int', '0'))
            data['episode_number'] = int(meta.get('episode_int', '0'))
        headers = {
            'User-Agent': f'Uploadrr / v1.0 ({platform.system()} {platform.release()})'
        }
        params = {
            'api_token' : self.config['TRACKERS'][self.tracker]['api_key'].strip()
        }
        
        if not meta['debug']:
            success = 'Unknown'
            try:
                response = requests.post(url=self.upload_url, files=files, data=data, headers=headers, params=params)
                response.raise_for_status()                
                response_json = response.json()
                success = response_json.get('success', False)
                data = response_json.get('data', {})
            except Exception as e:
                console.print(f"[red]Encountered Error: {e}[/red]\n[bold yellow]May have uploaded, please go check..")

            if success == 'Unknown':
                console.print("[bold yellow]Status of upload is unknown, please go check..")
                success = False
            elif success:
                console.print("[bold green]Torrent uploaded successfully!")
            else:
                console.print("[bold red]Torrent upload failed.")

            if data:
                if 'name' in data and 'The name has already been taken.' in data['name']:
                    console.print("[red]Name has already been taken.")
                if 'info_hash' in data and 'The info hash has already been taken.' in data['info_hash']:
                    console.print("[red]Info hash has already been taken.")                
            else:
                console.print("[cyan]Request Data:")
                console.print(data)
    
            try:
                open_torrent.close()
            except Exception as e:
                console.print(f"[red]Failed to close torrent file: {e}[/red]")

            return success 

    def get_language_tag(self, meta):
        soundmix = meta.get('imdb_info', {}).get('soundmix', [])
        is_silent = 'silent' in soundmix if soundmix else False 

        def map_language(language):
            try:
                lang_code = langcodes.find(language).to_alpha3()
                return lang_code.upper()
            except langcodes.LanguageTagError:
                return '???'

        audio_lang = []
        sub_lang = []
        if meta.get("is_disc") == "BDMV":
            if 'discs' in meta and meta['discs']:
                bdinfo = meta['discs'][0].get('bdinfo', {})
                audio_tracks = bdinfo.get('audio', [])
                subtitle_tracks = bdinfo.get('subtitles', [])
                
                for track in audio_tracks:
                    language = track.get('language')
                    if language and 'comment' not in language.lower() and 'review' not in language.lower():
                        audio_lang.append(map_language(language))

                audio_lang = list(dict.fromkeys(audio_lang))  # Remove dupes + keep order
                
                if not audio_lang:
                    audio_lang.append('???')
                
                if is_silent:
                    lang_tag = "[Silent]"
                else:    
                    lang_tag = f"[{' '.join(audio_lang)}]"
                
                for lang in subtitle_tracks:
                    sub_lang.append(map_language(lang))
                
                if not sub_lang:
                    sub_lang_tag = "[No Subs]"
                else:
                    sub_lang = list(dict.fromkeys(sub_lang))  # Remove dupes + keep order
                    if 'ENG' in sub_lang:
                        if len(sub_lang) > 1:
                            sub_lang_tag = "[Subs ENG+]"
                        else:
                            sub_lang_tag = "[Subs ENG]"
                    else:
                        if sub_lang[0] == '???':
                            sub_lang_tag = "[Subs ???]"
                        else:
                            if len(sub_lang) > 1:
                                sub_lang_tag = f"[Subs {sub_lang[0]}+]"
                            else:
                                sub_lang_tag = f"[Subs {sub_lang[0]}]"
        elif 'mediainfo' in meta:
            for x in meta["mediainfo"]["media"]["track"]:
                if x["@type"] == "Audio":
                    commentary_found = 'Title' in x and ('comment' in x['Title'].lower() or 'review' in x['Title'].lower())
                    if not commentary_found and 'Language_String3' in x:
                        audio_lang.append(x.get('Language_String3'))
            
            audio_lang = list(dict.fromkeys(audio_lang))  # Remove dupes + keep order
            if not audio_lang:
                audio_lang.append('???')
            if is_silent:
                lang_tag = "[Silent]"
            else:        
                lang_tag = f"[{' '.join(lang.upper() for lang in audio_lang)}]"
            
            sub_lang = [x.get('Language_String3') for x in meta["mediainfo"]["media"]["track"] if x["@type"] == "Text"]
            if not sub_lang:
                sub_lang_tag = "[No Subs]"
            else:
                sub_lang = list(dict.fromkeys(sub_lang))  # Remove dupes + keep order
                if 'eng' in sub_lang:
                    if len(sub_lang) > 1:
                        sub_lang_tag = "[Subs ENG+]"
                    else:
                        sub_lang_tag = "[Subs ENG]"
                else:
                    if sub_lang[0] is None:
                        sub_lang_tag = "[Subs ???]"
                    else:
                        if len(sub_lang) > 1:
                            sub_lang_tag = f"[Subs {sub_lang[0].upper()}+]"
                        else:
                            sub_lang_tag = f"[Subs {sub_lang[0].upper()}]"
        else:
            audio_lang.append('???')
            if is_silent:
                lang_tag = "[Silent]"
            else:    
                lang_tag = f"[{' '.join(audio_lang)}]"
            sub_lang_tag = "[No Subs]"

        return lang_tag + " " + sub_lang_tag



    def get_basename(self, meta):
        path = next(iter(meta['filelist']), meta['path'])
        return os.path.basename(path)
   
    async def get_name(self, meta):
        # Have to agree with whoever made HUNO's script
        # was easier to rebuild name with Prep.get_name() and mofidy 
        # than to attempt to edit the name thereafter - thanks for the tip

        basename = self.get_basename(meta)
        type = meta.get('type', "")
        title = meta.get('title',"")
        alt_title = meta.get('aka', "")
        year = meta.get('year', "")
        resolution = meta.get('resolution', "")
        if resolution == "OTHER":
            resolution = ""
        audio = meta.get('audio', "")
        lang_tag = self.get_language_tag(meta)
        service = meta.get('service', "")
        season = meta.get('season', "")
        episode = meta.get('episode', "")
        part = meta.get('part', "")
        repack = meta.get('repack', "")
        three_d = meta.get('3D', "")
        tag = meta.get('tag', "")
        if tag == "":
            tag = "-NOGRP"
        source = meta.get('source', "")
        uhd = meta.get('uhd', "")
        hdr = meta.get('hdr', "")
        episode_title = meta.get('episode_title', '')
        if meta.get('is_disc', "") == "BDMV": #Disk
            video_codec = meta.get('video_codec', "")
            region = meta.get('region', "")
        elif meta.get('is_disc', "") == "DVD":
            region = meta.get('region', "")
            dvd_size = meta.get('dvd_size', "")
        else:
            video_codec = meta.get('video_codec', "")
            video_encode = meta.get('video_encode', video_codec)
        edition = meta.get('edition', "")
        cut = meta.get('cut', "")
        ratio = meta.get('ratio', "")

        if meta['category'] == "TV":
            try:
                year = meta['year']
                if not year: 
                    raise ValueError("No TMDB Year Found..trying IMDB")
            except (KeyError, ValueError):
                try:
                    year = meta['imdb_info']['year']
                    if not year:
                        raise ValueError("No IMDB Year Found..")
                except (KeyError, ValueError):
                    year = ""
        if meta.get('no_season', False) is True:
            season = ''
        if meta.get('no_year', False) is True:
            year = ''
        if meta.get('no_aka', False) is True:
            alt_title = ''
        if meta['debug']:
            console.log("[cyan]get_name cat/type")
            console.log(f"CATEGORY: {meta['category']}")
            console.log(f"TYPE: {meta['type']}")
            console.log("[cyan]get_name meta:")
            console.log(meta)

        #YAY NAMING FUN
        if meta['category'] == "MOVIE": #MOVIE SPECIFIC
            if type == "DISC": #Disk
                if meta['is_disc'] == 'BDMV':
                    name = f"{title} {alt_title} ({year}) {three_d} [{cut} {ratio} {edition} {repack} {resolution} {region} {uhd} {source} {hdr} {video_codec} {audio}{tag}] {lang_tag}"
                    potential_missing = ['edition', 'region', 'distributor']
                elif meta['is_disc'] == 'DVD': 
                    name = f"{title} {alt_title} ({year}) [{cut} {ratio} {edition} {repack} {source} {dvd_size} {audio}{tag}] {lang_tag}"
                    potential_missing = ['edition', 'distributor']
                elif meta['is_disc'] == 'HDDVD':
                    name = f"{title} {alt_title} ({year}) [{cut} {ratio} {edition} {repack} {resolution} {source} {video_codec}] {audio}{tag}] {lang_tag}"
                    potential_missing = ['edition', 'region', 'distributor']
            elif type == "REMUX" and source in ("BluRay", "HDDVD"): #BluRay/HDDVD Remux
                name = f"{title} {alt_title} ({year}) {three_d} [{cut} {ratio} {edition} {repack} {resolution} {uhd} {source} REMUX {hdr} {video_codec} {audio}{tag}] {lang_tag}" 
                potential_missing = ['edition', 'description']
            elif type == "REMUX" and source in ("PAL DVD", "NTSC DVD", "DVD"): #DVD Remux
                name = f"{title} {alt_title} ({year}) [{cut} {ratio} {edition} {repack} {source} REMUX  {audio}{tag}] {lang_tag}" 
                potential_missing = ['edition', 'description']
            elif type == "ENCODE": #Encode
                name = f"{title} {alt_title} ({year}) [{cut} {ratio} {edition} {repack} {resolution} {uhd} {source} {audio} {hdr} {video_encode}{tag}] {lang_tag}"  
                potential_missing = ['edition', 'description']
            elif type == "WEBDL": #WEB-DL
                name = f"{title} {alt_title} ({year}) [{cut} {ratio} {edition} {repack} {resolution} {uhd} {service} WEB-DL {audio} {hdr} {video_encode}{tag}] {lang_tag}"
                potential_missing = ['edition', 'service']
            elif type == "WEBRIP": #WEBRip
                name = f"{title} {alt_title} ({year}) [{cut} {ratio} {edition} {repack} {resolution} {uhd} {service} WEBRip {audio} {hdr} {video_encode}{tag}] {lang_tag}"
                potential_missing = ['edition', 'service']
            elif type == "HDTV": #HDTV
                name = f"{title} {alt_title} ({year}) [{cut} {ratio} {edition} {repack} {resolution} {source} {audio} {video_encode}{tag}] {lang_tag}"
                potential_missing = []
        elif meta['category'] == "TV": #TV SPECIFIC
            if type == "DISC": #Disk
                if meta['is_disc'] == 'BDMV':
                    name = f"{title} ({year}) {alt_title} {season}{episode} {three_d} [{cut} {ratio} {edition} {repack} {resolution} {region} {uhd} {source} {hdr} {video_codec} {audio}{tag}] {lang_tag}"
                    potential_missing = ['edition', 'region', 'distributor']
                if meta['is_disc'] == 'DVD':
                    name = f"{title} {alt_title} {season}{episode} {three_d} [{cut} {ratio} {edition} {repack} {source} {dvd_size} {audio}{tag}] {lang_tag}"
                    potential_missing = ['edition', 'distributor']
                elif meta['is_disc'] == 'HDDVD':
                    name = f"{title} {alt_title} ({year}) [{cut} {ratio} {edition} {repack} {resolution} {source} {video_codec} {audio}{tag}] {lang_tag}"
                    potential_missing = ['edition', 'region', 'distributor']
            elif type == "REMUX" and source in ("BluRay", "HDDVD"): #BluRay Remux
                name = f"{title} ({year}) {alt_title} {season}{episode} {episode_title} {part} [{three_d} {cut} {ratio} {edition} {repack} {resolution} {uhd} {source} REMUX {hdr} {video_codec} {audio}{tag}] {lang_tag}" #SOURCE
                potential_missing = ['edition', 'description']
            elif type == "REMUX" and source in ("PAL DVD", "NTSC DVD"): #DVD Remux
                name = f"{title} ({year}) {alt_title} {season}{episode} {episode_title} {part} [{cut} {ratio} {edition} {repack} {source} REMUX {audio}{tag}] {lang_tag}" #SOURCE
                potential_missing = ['edition', 'description']
            elif type == "ENCODE": #Encode
                name = f"{title} ({year}) {alt_title} {season}{episode} {episode_title} {part} [{cut} {ratio} {edition} {repack} {resolution} {uhd} {source} {audio} {hdr} {video_encode}{tag}] {lang_tag}" #SOURCE
                potential_missing = ['edition', 'description']
            elif type == "WEBDL": #WEB-DL
                name = f"{title} ({year}) {alt_title} {season}{episode} {episode_title} {part} [{cut} {ratio} {edition} {repack} {resolution} {uhd} {service} WEB-DL {audio} {hdr} {video_encode}{tag}] {lang_tag}"
                potential_missing = ['edition', 'service']
            elif type == "WEBRIP": #WEBRip
                name = f"{title} ({year}) {alt_title} {season}{episode} {episode_title} {part} [{cut} {ratio} {edition} {repack} {resolution} {uhd} {service} WEBRip {audio} {hdr} {video_encode}{tag}] {lang_tag}"
                potential_missing = ['edition', 'service']
            elif type == "HDTV": #HDTV
                name = f"{title} ({year}) {alt_title} {season}{episode} {episode_title} {part} [{cut} {ratio} {edition} {repack} {resolution} {source} {audio} {video_encode}{tag}] {lang_tag}"
                potential_missing = []

        parts = name.split()
        if '[' in parts:        
            bracket_index = parts.index('[')
            sq_bracket = next((i for i, part in enumerate(parts[bracket_index+1:]) if part.strip()), None)
            if sq_bracket is not None:
                name = ' '.join(parts[:bracket_index+1]) + ' '.join(parts[bracket_index+1:])
        
        return ' '.join(name.split())
    

    async def search_existing(self, meta):
        dupes = {}
        console.print("[yellow]Searching for existing torrents on site...")
        params = {
            'api_token': self.config['TRACKERS'][self.tracker]['api_key'].strip(),
            'tmdbId': meta['tmdb'],
            'categories[]': await self.get_cat_id(meta['category'], meta.get('genres', ''), meta.get('keywords', ''), meta.get('service', ''), meta.get('edition', ''), meta),
            'types[]': await self.get_type_id(meta['type'], meta['edition']),
            'resolutions[]': await self.get_res_id(meta['resolution']),
            'name': ""
        }
        if meta.get('edition', "") != "":
            params['name'] = params['name'] + f" {meta['edition']}"
        try:
            response = requests.get(url=self.search_url, params=params)
            response = response.json()
            for each in response['data']:
                result = each['attributes']['name']
                split_result = re.split(r'(-\w*\])', result)
                if len(split_result) > 1:
                    result = split_result[0] + split_result[1]
                size = each['attributes']['size']
                if "🔥Eternal" not in result:
                    dupes[result] = size
        except Exception as e:
            console.print(f'[bold red]Unable to search for existing torrents on site. Either the site is down or your API key is incorrect. Error: {e}')
            await asyncio.sleep(5)

        return dupes


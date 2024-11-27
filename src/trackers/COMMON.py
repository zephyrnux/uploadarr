from torf import Torrent
import os
import traceback
import requests
import re
import json
import aiofiles

from src.bbcode import BBCODE
from src.console import console
from rich import print

class COMMON():
    def __init__(self, config):
        self.config = config
        pass

    async def edit_torrent(self, meta, tracker, source_flag, torrent_filename="BASE"):
        if os.path.exists(f"{meta['base_dir']}/tmp/{meta['uuid']}/{torrent_filename}.torrent"):
            new_torrent = Torrent.read(f"{meta['base_dir']}/tmp/{meta['uuid']}/{torrent_filename}.torrent")
            for each in list(new_torrent.metainfo):
                if each not in ('announce', 'comment', 'creation date', 'created by', 'encoding', 'info'):
                    new_torrent.metainfo.pop(each, None)
            new_torrent.metainfo['announce'] = self.config['TRACKERS'][tracker].get('announce_url', "https://fake.tracker").strip()
            new_torrent.metainfo['info']['source'] = source_flag
            Torrent.copy(new_torrent).write(f"{meta['base_dir']}/tmp/{meta['uuid']}/[{tracker}]{meta['clean_name']}.torrent", overwrite=True)

    # used to add tracker url, comment and source flag to torrent file
    async def add_tracker_torrent(self, meta, tracker, source_flag, new_tracker, comment):
        if os.path.exists(f"{meta['base_dir']}/tmp/{meta['uuid']}/BASE.torrent"):
            new_torrent = Torrent.read(f"{meta['base_dir']}/tmp/{meta['uuid']}/BASE.torrent")
            new_torrent.metainfo['announce'] = new_tracker
            new_torrent.metainfo['comment'] = comment
            new_torrent.metainfo['info']['source'] = source_flag
            Torrent.copy(new_torrent).write(f"{meta['base_dir']}/tmp/{meta['uuid']}/[{tracker}]{meta['clean_name']}.torrent", overwrite=True)
    

    async def read_log_file(self, log_file):
        try:
            async with aiofiles.open(log_file, 'rb') as log:
                raw_data = await log.read() 
                try:
                    log_contents = raw_data.decode('utf-16')
                except UnicodeDecodeError:
                    log_contents = raw_data.decode('utf-8', errors='ignore')
                
                return log_contents
        except Exception as e:
            return f"Error reading log file: {str(e)}"

    async def unit3d_edit_desc(self, meta, tracker, comparison=False, desc_header=""):
        async with aiofiles.open(f"{meta['base_dir']}/tmp/{meta['uuid']}/DESCRIPTION.txt", 'r', encoding='utf-8') as basefile:
            base = await basefile.read() 

        async with aiofiles.open(f"{meta['base_dir']}/tmp/{meta['uuid']}/[{tracker}]DESCRIPTION.txt", 'w', encoding='utf-8') as descfile:
            if desc_header != "":
                await descfile.write(desc_header)

            bbcode = BBCODE()
            if meta.get('discs', []):
                discs = meta['discs']
                if discs[0]['type'] == "DVD":
                    await descfile.write(f"[spoiler=VOB MediaInfo][code]{discs[0]['vob_mi']}[/code][/spoiler]\n")
                    await descfile.write("\n")
                if len(discs) >= 2:
                    for each in discs[1:]:
                        if each['type'] == "BDMV":
                            await descfile.write(f"[spoiler={each.get('name', 'BDINFO')}][code]{each['summary']}[/code][/spoiler]\n")
                            await descfile.write("\n")
                        elif each['type'] == "DVD":
                            await descfile.write(f"{each['name']}:\n")
                            await descfile.write(f"[spoiler={os.path.basename(each['vob'])}][code][{each['vob_mi']}[/code][/spoiler] [spoiler={os.path.basename(each['ifo'])}][code][{each['ifo_mi']}[/code][/spoiler]\n")
                            await descfile.write("\n")
                        elif each['type'] == "HDDVD":
                            await descfile.write(f"{each['name']}:\n")
                            await descfile.write(f"[spoiler={os.path.basename(each['largest_evo'])}][code][{each['evo_mi']}[/code][/spoiler]\n")
                            await descfile.write("\n")
            
            # Process BBCode
            desc = bbcode.convert_pre_to_code(base)
            desc = bbcode.convert_hide_to_spoiler(desc)
            if tracker in ('LDU', 'DEV'):
                comparison = True

            if not comparison:
                desc = bbcode.convert_comparison_to_collapse(desc, 1000)

            # Handle music-related content
            if meta.get('is_music', False):
                album_cover = meta.get('album_cover', None)
                album_back = meta.get('album_back', None)
                display_cover = self.config["DEFAULT"].get('album_covers', 2)

                if display_cover == 1:
                    if album_cover:
                        await descfile.write(f"[center][img]{album_cover}[/img][/center]\n\n")
                elif display_cover >= 2:
                    if album_cover:
                        await descfile.write(f"[center][img]{album_cover}[/img]")
                        if album_back:  
                            await descfile.write(f" [img]{album_back}[/img]")
                        await descfile.write("[/center]\n\n")
                    elif album_back:  
                        await descfile.write(f"[center][img]{album_back}[/img][/center]\n\n")
                proof = meta.get('album_proof')
                if proof:
                    await descfile.write(f"[center][spoiler=Proof][img=500]{proof}[/img][/spoiler][/center]\n\n")


                mbid = meta.get('mbid', False)
                if mbid:
                    await descfile.write(f"[center][url=https://musicbrainz.org/release/{mbid}][img=120]https://upload.wikimedia.org/wikipedia/commons/f/f2/MusicBrainz_Logo_Mini_%282016%29.svg[/img][/url][/center]")
                discogs_id = meta.get('discogs_id', False)
                discogs_url = meta.get('discogs_url', False)
                if discogs_id:
                    discogs = f'https://www.discogs.com/release/{discogs_id}'
                elif discogs_url:
                    discogs = discogs_url
                else:
                    discogs = None                
                if discogs:
                    await descfile.write(f"[center][url={discogs}][img=120]https://upload.wikimedia.org/wikipedia/commons/thumb/c/ce/Discogs_logo_black.svg/2880px-Discogs_logo_black.svg.png[/img][/url][/center]") 
                allmusic = meta.get('allmusic', False)
                if allmusic:
                    await descfile.write(f"[center][url={allmusic}][img=120]https://upload.wikimedia.org/wikipedia/commons/thumb/0/03/AllMusic_Text_Logo.svg/2880px-AllMusic_Text_Logo.svg.png[/img][/url][/center]")
                wikidata = meta.get('wikidata', False)
                if wikidata:
                    await descfile.write(f"[center][url={wikidata}][img=120]https://upload.wikimedia.org/wikipedia/commons/6/66/Wikidata-logo-en.svg[/img][/url][/center]") 
                genius = meta.get('genius', False)
                if genius:
                    await descfile.write(f"[center][url={genius}][img=120]https://upload.wikimedia.org/wikipedia/commons/c/cd/Genius-Wordmark.svg[/img][/url][/center]")    
                                         
                tracks = meta.get('tracklist', {})
                log_file = meta.get('log_file')

                if tracks:
                    await descfile.write("\n[code][h5]TRACKLIST[/h5]\n")
                    if len(tracks) > 1:
                        for disc, disc_tracks in tracks.items():
                            await descfile.write(f"[u]{disc}[/u]\n")

                            # Calculate the maximum track length for this disc
                            max_track_length = max(len(track) for track in disc_tracks)

                            for track, time in disc_tracks.items():
                                track_length = len(track)

                                # Calculate the padding needed based on the longest track
                                # Ensure there's at least a 2 character buffer between the track name and the timestamp
                                padding_length = max(0, max_track_length - track_length + 2)

                                # Write the track name with appropriate padding
                                await descfile.write(f"{track}")
                                await descfile.write(" " * padding_length)
                                await descfile.write(f"[{time}]\n")

                            await descfile.write("\n")  # Add a newline for separation between discs
                    else:
                        for track, time in next(iter(tracks.values())).items():
                            track_length = len(track)
                            length = max(0, 52 - track_length)
                            await descfile.write(f"{track}")
                            await descfile.write(" " * length)
                            await descfile.write(f"[{time}]\n")

                    if log_file:
                        log_contents = await self.read_log_file(log_file)
                        if log_contents:
                            await descfile.write(f"\n[spoiler=log][code]{log_contents}[/code][/spoiler]")

                    # Close the TRACKLIST [code] block after the log
                    await descfile.write("[/code]\n")

                elif log_file:
                    # Handle the case where there are no tracks but a log exists
                    log_contents = await self.read_log_file(log_file)
                    if log_contents:
                        await descfile.write(f"\n[spoiler=log][code]{log_contents}[/code][/spoiler]")


                if album_cover:
                    await descfile.write(f"[url=torrent-cover={album_cover} ][/url]")    

            # Handle video trailers and logos
            if tracker not in ('AITHER', 'CBR', 'OE'):
                add_trailer_enabled = self.config["DEFAULT"].get("add_trailer", False)    
                if add_trailer_enabled and meta.get("category") == "MOVIE":
                    key = meta.get("youtube")
                    if key:
                        await descfile.write(f"[center][youtube]{key}[/youtube][/center]")

            add_logo_enabled = self.config["DEFAULT"].get("add_logo", False)
            if add_logo_enabled:
                logo = meta.get('logo')
                logo_size = self.config["DEFAULT"].get("logo_size", 420)
                if logo:
                    await descfile.write(f"[center][img={logo_size}]{logo}[/img][/center]")  

            img_size = self.config["DEFAULT"].get("img_size", 500)
            if tracker == "CBR":
                img_size = 350
            inline_imgs = self.config["DEFAULT"].get("inline_imgs", 0)
            await descfile.write(desc)
            images = meta['image_list']
            if images: 
                await descfile.write(f"\n[center]")
                for each in range(len(images[:int(meta['screens'])])):
                    web_url = images[each]['web_url']
                    raw_url = images[each]['raw_url']
                    await descfile.write(f"[url={web_url}][img={img_size}]{raw_url}[/img][/url] ")
                    if img_size and inline_imgs:
                        try:
                            inline_imgs = int(inline_imgs) 
                            if each % inline_imgs == inline_imgs - 1:
                                await descfile.write("\n")
                        except ValueError:
                            print("[bold][red]WARN[/red]: Invalid value given for inline_imgs in config.[/bold]")
                await descfile.write("[/center]")

            # Global signature handling
            use_global_sigs = self.config["DEFAULT"].get("use_global_sigs", False)
            if use_global_sigs:
                signature = self.config["DEFAULT"].get("global_sig")
                anon_signature = self.config["DEFAULT"].get("global_anon_sig")
                pr_signature = self.config["DEFAULT"].get("global_pr_sig")
                anon_pr_sig = self.config["DEFAULT"].get("global_anon_pr_sig")
                if signature is None or anon_signature is None or pr_signature is None or anon_pr_sig is None:
                    print("[bold][red]WARN[/red]: Global signatures are enabled but not provided in config.[/bold]")                
            else:
                signature = self.config["TRACKERS"][tracker].get("signature")
                anon_signature = self.config["TRACKERS"][tracker].get("anon_signature")
                pr_signature = self.config["TRACKERS"][tracker].get("pr_signature")
                anon_pr_sig = self.config["TRACKERS"][tracker].get("anon_pr_signature")
                if signature is None or anon_signature is None or pr_signature is None or anon_pr_sig is None:
                    print("[bold][red]WARN[/red]: Global Signatures are turned off, but no signature is provided for selected tracker.[/bold]")

        async with aiofiles.open(f"{meta['base_dir']}/tmp/{meta['uuid']}/[{tracker}]DESCRIPTION.txt", 'a', encoding='utf-8') as descfile:
            if meta["personalrelease"]:
                if meta["anon"] != 0 or self.config["TRACKERS"][tracker].get("anon", False):
                    await descfile.write("\n" + anon_pr_sig)
                elif meta["anon"] == 0:
                    await descfile.write("\n" + pr_signature)
            else:
                if meta["anon"] != 0 or self.config["TRACKERS"][tracker].get("anon", False):
                    await descfile.write("\n" + anon_signature)
                elif meta["anon"] == 0:
                    await descfile.write("\n" + signature)

        return
    
    
    async def unit3d_region_ids(self, region):
        region_id = {
            'AFG': 1, 'AIA': 2, 'ALA': 3, 'ALG': 4, 'AND': 5, 'ANG': 6, 'ARG': 7, 'ARM': 8, 'ARU': 9, 
            'ASA': 10, 'ATA': 11, 'ATF': 12, 'ATG': 13, 'AUS': 14, 'AUT': 15, 'AZE': 16, 'BAH': 17, 
            'BAN': 18, 'BDI': 19, 'BEL': 20, 'BEN': 21, 'BER': 22, 'BES': 23, 'BFA': 24, 'BHR': 25, 
            'BHU': 26, 'BIH': 27, 'BLM': 28, 'BLR': 29, 'BLZ': 30, 'BOL': 31, 'BOT': 32, 'BRA': 33, 
            'BRB': 34, 'BRU': 35, 'BVT': 36, 'CAM': 37, 'CAN': 38, 'CAY': 39, 'CCK': 40, 'CEE': 41, 
            'CGO': 42, 'CHA': 43, 'CHI': 44, 'CHN': 45, 'CIV': 46, 'CMR': 47, 'COD': 48, 'COK': 49, 
            'COL': 50, 'COM': 51, 'CPV': 52, 'CRC': 53, 'CRO': 54, 'CTA': 55, 'CUB': 56, 'CUW': 57, 
            'CXR': 58, 'CYP': 59, 'DJI': 60, 'DMA': 61, 'DOM': 62, 'ECU': 63, 'EGY': 64, 'ENG': 65, 
            'EQG': 66, 'ERI': 67, 'ESH': 68, 'ESP': 69, 'ETH': 70, 'FIJ': 71, 'FLK': 72, 'FRA': 73, 
            'FRO': 74, 'FSM': 75, 'GAB': 76, 'GAM': 77, 'GBR': 78, 'GEO': 79, 'GER': 80, 'GGY': 81, 
            'GHA': 82, 'GIB': 83, 'GLP': 84, 'GNB': 85, 'GRE': 86, 'GRL': 87, 'GRN': 88, 'GUA': 89, 
            'GUF': 90, 'GUI': 91, 'GUM': 92, 'GUY': 93, 'HAI': 94, 'HKG': 95, 'HMD': 96, 'HON': 97, 
            'HUN': 98, 'IDN': 99, 'IMN': 100, 'IND': 101, 'IOT': 102, 'IRL': 103, 'IRN': 104, 'IRQ': 105, 
            'ISL': 106, 'ISR': 107, 'ITA': 108, 'JAM': 109, 'JEY': 110, 'JOR': 111, 'JPN': 112, 'KAZ': 113, 
            'KEN': 114, 'KGZ': 115, 'KIR': 116, 'KNA': 117, 'KOR': 118, 'KSA': 119, 'KUW': 120, 'KVX': 121, 
            'LAO': 122, 'LBN': 123, 'LBR': 124, 'LBY': 125, 'LCA': 126, 'LES': 127, 'LIE': 128, 'LKA': 129, 
            'LUX': 130, 'MAC': 131, 'MAD': 132, 'MAF': 133, 'MAR': 134, 'MAS': 135, 'MDA': 136, 'MDV': 137, 
            'MEX': 138, 'MHL': 139, 'MKD': 140, 'MLI': 141, 'MLT': 142, 'MNG': 143, 'MNP': 144, 'MON': 145, 
            'MOZ': 146, 'MRI': 147, 'MSR': 148, 'MTN': 149, 'MTQ': 150, 'MWI': 151, 'MYA': 152, 'MYT': 153, 
            'NAM': 154, 'NCA': 155, 'NCL': 156, 'NEP': 157, 'NFK': 158, 'NIG': 159, 'NIR': 160, 'NIU': 161, 
            'NLD': 162, 'NOR': 163, 'NRU': 164, 'NZL': 165, 'OMA': 166, 'PAK': 167, 'PAN': 168, 'PAR': 169, 
            'PCN': 170, 'PER': 171, 'PHI': 172, 'PLE': 173, 'PLW': 174, 'PNG': 175, 'POL': 176, 'POR': 177, 
            'PRK': 178, 'PUR': 179, 'QAT': 180, 'REU': 181, 'ROU': 182, 'RSA': 183, 'RUS': 184, 'RWA': 185, 
            'SAM': 186, 'SCO': 187, 'SDN': 188, 'SEN': 189, 'SEY': 190, 'SGS': 191, 'SHN': 192, 'SIN': 193, 
            'SJM': 194, 'SLE': 195, 'SLV': 196, 'SMR': 197, 'SOL': 198, 'SOM': 199, 'SPM': 200, 'SRB': 201, 
            'SSD': 202, 'STP': 203, 'SUI': 204, 'SUR': 205, 'SWZ': 206, 'SXM': 207, 'SYR': 208, 'TAH': 209, 
            'TAN': 210, 'TCA': 211, 'TGA': 212, 'THA': 213, 'TJK': 214, 'TKL': 215, 'TKM': 216, 'TLS': 217, 
            'TOG': 218, 'TRI': 219, 'TUN': 220, 'TUR': 221, 'TUV': 222, 'TWN': 223, 'UAE': 224, 'UGA': 225, 
            'UKR': 226, 'UMI': 227, 'URU': 228, 'USA': 229, 'UZB': 230, 'VAN': 231, 'VAT': 232, 'VEN': 233, 
            'VGB': 234, 'VIE': 235, 'VIN': 236, 'VIR': 237, 'WAL': 238, 'WLF': 239, 'YEM': 240, 'ZAM': 241, 
            'ZIM': 242, 'EUR' : 243
        }.get(region, 0)
        return region_id

    async def unit3d_distributor_ids(self, distributor):
        distributor_id = {
            '01 DISTRIBUTION': 1, '100 DESTINATIONS TRAVEL FILM': 2, '101 FILMS': 3, '1FILMS': 4, '2 ENTERTAIN VIDEO': 5, '20TH CENTURY FOX': 6, '2L': 7, '3D CONTENT HUB': 8, '3D MEDIA': 9, '3L FILM': 10, '4DIGITAL': 11, '4DVD': 12, '4K ULTRA HD MOVIES': 13, '4K UHD': 13, '8-FILMS': 14, '84 ENTERTAINMENT': 15, '88 FILMS': 16, '@ANIME': 17, 'ANIME': 17, 'A CONTRACORRIENTE': 18, 'A CONTRACORRIENTE FILMS': 19, 'A&E HOME VIDEO': 20, 'A&E': 20, 'A&M RECORDS': 21, 'A+E NETWORKS': 22, 'A+R': 23, 'A-FILM': 24, 'AAA': 25, 'AB VIDÉO': 26, 'AB VIDEO': 26, 'ABC - (AUSTRALIAN BROADCASTING CORPORATION)': 27, 'ABC': 27, 'ABKCO': 28, 'ABSOLUT MEDIEN': 29, 'ABSOLUTE': 30, 'ACCENT FILM ENTERTAINMENT': 31, 'ACCENTUS': 32, 'ACORN MEDIA': 33, 'AD VITAM': 34, 'ADA': 35, 'ADITYA VIDEOS': 36, 'ADSO FILMS': 37, 'AFM RECORDS': 38, 'AGFA': 39, 'AIX RECORDS': 40, 'ALAMODE FILM': 41, 'ALBA RECORDS': 42, 'ALBANY RECORDS': 43, 'ALBATROS': 44, 'ALCHEMY': 45, 'ALIVE': 46, 'ALL ANIME': 47, 'ALL INTERACTIVE ENTERTAINMENT': 48, 'ALLEGRO': 49, 'ALLIANCE': 50, 'ALPHA MUSIC': 51, 'ALTERDYSTRYBUCJA': 52, 'ALTERED INNOCENCE': 53, 'ALTITUDE FILM DISTRIBUTION': 54, 'ALUCARD RECORDS': 55, 'AMAZING D.C.': 56, 'AMAZING DC': 56, 'AMMO CONTENT': 57, 'AMUSE SOFT ENTERTAINMENT': 58, 'ANCONNECT': 59, 'ANEC': 60, 'ANIMATSU': 61, 'ANIME HOUSE': 62, 'ANIME LTD': 63, 'ANIME WORKS': 64, 'ANIMEIGO': 65, 'ANIPLEX': 66, 'ANOLIS ENTERTAINMENT': 67, 'ANOTHER WORLD ENTERTAINMENT': 68, 'AP INTERNATIONAL': 69, 'APPLE': 70, 'ARA MEDIA': 71, 'ARBELOS': 72, 'ARC ENTERTAINMENT': 73, 'ARP SÉLECTION': 74, 'ARP SELECTION': 74, 'ARROW': 75, 'ART SERVICE': 76, 'ART VISION': 77, 'ARTE ÉDITIONS': 78, 'ARTE EDITIONS': 78, 'ARTE VIDÉO': 79, 'ARTE VIDEO': 79, 'ARTHAUS MUSIK': 80, 'ARTIFICIAL EYE': 81, 'ARTSPLOITATION FILMS': 82, 'ARTUS FILMS': 83, 'ASCOT ELITE HOME ENTERTAINMENT': 84, 'ASIA VIDEO': 85, 'ASMIK ACE': 86, 'ASTRO RECORDS & FILMWORKS': 87, 'ASYLUM': 88, 'ATLANTIC FILM': 89, 'ATLANTIC RECORDS': 90, 'ATLAS FILM': 91, 'AUDIO VISUAL ENTERTAINMENT': 92, 'AURO-3D CREATIVE LABEL': 93, 'AURUM': 94, 'AV VISIONEN': 95, 'AV-JET': 96, 'AVALON': 97, 'AVENTI': 98, 'AVEX TRAX': 99, 'AXIOM': 100, 'AXIS RECORDS': 101, 'AYNGARAN': 102, 'BAC FILMS': 103, 'BACH FILMS': 104, 'BANDAI VISUAL': 105, 'BARCLAY': 106, 'BBC': 107, 'BRITISH BROADCASTING CORPORATION': 107, 'BBI FILMS': 108, 'BBI': 108, 'BCI HOME ENTERTAINMENT': 109, 'BEGGARS BANQUET': 110, 'BEL AIR CLASSIQUES': 111, 'BELGA FILMS': 112, 'BELVEDERE': 113, 'BENELUX FILM DISTRIBUTORS': 114, 'BENNETT-WATT MEDIA': 115, 'BERLIN CLASSICS': 116, 'BERLINER PHILHARMONIKER RECORDINGS': 117, 'BEST ENTERTAINMENT': 118, 'BEYOND HOME ENTERTAINMENT': 119, 'BFI VIDEO': 120, 'BFI': 120, 'BRITISH FILM INSTITUTE': 120, 'BFS ENTERTAINMENT': 121, 'BFS': 121, 'BHAVANI': 122, 'BIBER RECORDS': 123, 'BIG HOME VIDEO': 124, 'BILDSTÖRUNG': 125, 'BILDSTORUNG': 125, 'BILL ZEBUB': 126, 'BIRNENBLATT': 127, 'BIT WEL': 128, 'BLACK BOX': 129, 'BLACK HILL PICTURES': 130, 'BLACK HILL': 130, 'BLACK HOLE RECORDINGS': 131, 'BLACK HOLE': 131, 'BLAQOUT': 132, 'BLAUFIELD MUSIC': 133, 'BLAUFIELD': 133, 'BLOCKBUSTER ENTERTAINMENT': 134, 'BLOCKBUSTER': 134, 'BLU PHASE MEDIA': 135, 'BLU-RAY ONLY': 136, 'BLU-RAY': 136, 'BLURAY ONLY': 136, 'BLURAY': 136, 'BLUE GENTIAN RECORDS': 137, 'BLUE KINO': 138, 'BLUE UNDERGROUND': 139, 'BMG/ARISTA': 140, 'BMG': 140, 'BMGARISTA': 140, 'BMG ARISTA': 140, 'ARISTA': 
            140, 'ARISTA/BMG': 140, 'ARISTABMG': 140, 'ARISTA BMG': 140, 'BONTON FILM': 141, 'BONTON': 141, 'BOOMERANG PICTURES': 142, 'BOOMERANG': 142, 'BQHL ÉDITIONS': 143, 'BQHL EDITIONS': 143, 'BQHL': 143, 'BREAKING GLASS': 144, 'BRIDGESTONE': 145, 'BRINK': 146, 'BROAD GREEN PICTURES': 147, 'BROAD GREEN': 147, 'BUSCH MEDIA GROUP': 148, 'BUSCH': 148, 'C MAJOR': 149, 'C.B.S.': 150, 'CAICHANG': 151, 'CALIFÓRNIA FILMES': 152, 'CALIFORNIA FILMES': 152, 'CALIFORNIA': 152, 'CAMEO': 153, 'CAMERA OBSCURA': 154, 'CAMERATA': 155, 'CAMP MOTION PICTURES': 156, 'CAMP MOTION': 156, 'CAPELIGHT PICTURES': 157, 'CAPELIGHT': 157, 'CAPITOL': 159, 'CAPITOL RECORDS': 159, 'CAPRICCI': 160, 'CARGO RECORDS': 161, 'CARLOTTA FILMS': 162, 'CARLOTTA': 162, 'CARLOTA': 162, 'CARMEN FILM': 163, 'CASCADE': 164, 'CATCHPLAY': 165, 'CAULDRON FILMS': 166, 'CAULDRON': 166, 'CBS TELEVISION STUDIOS': 167, 'CBS': 167, 'CCTV': 168, 'CCV ENTERTAINMENT': 169, 'CCV': 169, 'CD BABY': 170, 'CD LAND': 171, 'CECCHI GORI': 172, 'CENTURY MEDIA': 173, 'CHUAN XUN SHI DAI MULTIMEDIA': 174, 'CINE-ASIA': 175, 'CINÉART': 176, 'CINEART': 176, 'CINEDIGM': 177, 'CINEFIL IMAGICA': 178, 'CINEMA EPOCH': 179, 'CINEMA GUILD': 180, 'CINEMA LIBRE STUDIOS': 181, 'CINEMA MONDO': 182, 'CINEMATIC VISION': 183, 'CINEPLOIT RECORDS': 184, 'CINESTRANGE EXTREME': 185, 'CITEL VIDEO': 186, 'CITEL': 186, 'CJ ENTERTAINMENT': 187, 'CJ': 187, 'CLASSIC MEDIA': 188, 'CLASSICFLIX': 189, 'CLASSICLINE': 190, 'CLAUDIO RECORDS': 191, 'CLEAR VISION': 192, 'CLEOPATRA': 193, 'CLOSE UP': 194, 'CMS MEDIA LIMITED': 195, 'CMV LASERVISION': 196, 'CN ENTERTAINMENT': 197, 'CODE RED': 198, 'COHEN MEDIA GROUP': 199, 'COHEN': 199, 'COIN DE MIRE CINÉMA': 200, 'COIN DE MIRE CINEMA': 200, 'COLOSSEO FILM': 201, 'COLUMBIA': 203, 'COLUMBIA PICTURES': 203, 'COLUMBIA/TRI-STAR': 204, 'TRI-STAR': 204, 'COMMERCIAL MARKETING': 205, 'CONCORD MUSIC GROUP': 206, 'CONCORDE VIDEO': 207, 'CONDOR': 208, 'CONSTANTIN FILM': 209, 'CONSTANTIN': 209, 'CONSTANTINO FILMES': 210, 'CONSTANTINO': 210, 'CONSTRUCTIVE MEDIA SERVICE': 211, 'CONSTRUCTIVE': 211, 'CONTENT ZONE': 212, 'CONTENTS GATE': 213, 'COQUEIRO VERDE': 214, 'CORNERSTONE MEDIA': 215, 'CORNERSTONE': 215, 'CP DIGITAL': 216, 'CREST MOVIES': 217, 'CRITERION': 218, 'CRITERION COLLECTION': 
            218, 'CC': 218, 'CRYSTAL CLASSICS': 219, 'CULT EPICS': 220, 'CULT FILMS': 221, 'CULT VIDEO': 222, 'CURZON FILM WORLD': 223, 'D FILMS': 224, "D'AILLY COMPANY": 225, 'DAILLY COMPANY': 225, 'D AILLY COMPANY': 225, "D'AILLY": 225, 'DAILLY': 225, 'D AILLY': 225, 'DA CAPO': 226, 'DA MUSIC': 227, "DALL'ANGELO PICTURES": 228, 'DALLANGELO PICTURES': 228, "DALL'ANGELO": 228, 'DALL ANGELO PICTURES': 228, 'DALL ANGELO': 228, 'DAREDO': 229, 'DARK FORCE ENTERTAINMENT': 230, 'DARK FORCE': 230, 'DARK SIDE RELEASING': 231, 'DARK SIDE': 231, 'DAZZLER MEDIA': 232, 'DAZZLER': 232, 'DCM PICTURES': 233, 'DCM': 233, 'DEAPLANETA': 234, 'DECCA': 235, 'DEEPJOY': 236, 'DEFIANT SCREEN ENTERTAINMENT': 237, 'DEFIANT SCREEN': 237, 'DEFIANT': 237, 'DELOS': 238, 'DELPHIAN RECORDS': 239, 'DELPHIAN': 239, 'DELTA MUSIC & ENTERTAINMENT': 240, 'DELTA MUSIC AND ENTERTAINMENT': 240, 'DELTA MUSIC ENTERTAINMENT': 240, 'DELTA MUSIC': 240, 'DELTAMAC CO. LTD.': 241, 'DELTAMAC CO LTD': 241, 'DELTAMAC CO': 241, 'DELTAMAC': 241, 'DEMAND MEDIA': 242, 'DEMAND': 242, 'DEP': 243, 'DEUTSCHE GRAMMOPHON': 244, 'DFW': 245, 'DGM': 246, 'DIAPHANA': 247, 'DIGIDREAMS STUDIOS': 248, 'DIGIDREAMS': 248, 'DIGITAL ENVIRONMENTS': 249, 'DIGITAL': 249, 'DISCOTEK MEDIA': 250, 'DISCOVERY CHANNEL': 251, 'DISCOVERY': 251, 'DISK KINO': 252, 'DISNEY / BUENA VISTA': 253, 'DISNEY': 253, 'BUENA VISTA': 253, 'DISNEY BUENA VISTA': 253, 'DISTRIBUTION SELECT': 254, 'DIVISA': 255, 'DNC ENTERTAINMENT': 256, 'DNC': 256, 'DOGWOOF': 257, 'DOLMEN HOME VIDEO': 258, 'DOLMEN': 258, 'DONAU FILM': 259, 'DONAU': 259, 'DORADO FILMS': 260, 'DORADO': 260, 'DRAFTHOUSE FILMS': 261, 'DRAFTHOUSE': 261, 'DRAGON FILM ENTERTAINMENT': 262, 'DRAGON ENTERTAINMENT': 262, 'DRAGON FILM': 262, 'DRAGON': 262, 'DREAMWORKS': 263, 'DRIVE ON RECORDS': 264, 'DRIVE ON': 264, 'DRIVE-ON': 264, 'DRIVEON': 264, 'DS MEDIA': 265, 'DTP ENTERTAINMENT AG': 266, 'DTP ENTERTAINMENT': 266, 'DTP AG': 266, 'DTP': 266, 'DTS ENTERTAINMENT': 267, 'DTS': 267, 'DUKE MARKETING': 268, 'DUKE VIDEO DISTRIBUTION': 269, 'DUKE': 269, 'DUTCH FILMWORKS': 270, 'DUTCH': 270, 'DVD INTERNATIONAL': 271, 'DVD': 271, 'DYBEX': 272, 'DYNAMIC': 273, 'DYNIT': 274, 'E1 ENTERTAINMENT': 275, 'E1': 275, 'EAGLE ENTERTAINMENT': 276, 'EAGLE HOME ENTERTAINMENT PVT.LTD.': 
            277, 'EAGLE HOME ENTERTAINMENT PVTLTD': 277, 'EAGLE HOME ENTERTAINMENT PVT LTD': 277, 'EAGLE HOME ENTERTAINMENT': 277, 'EAGLE PICTURES': 278, 'EAGLE ROCK ENTERTAINMENT': 279, 'EAGLE ROCK': 279, 'EAGLE VISION MEDIA': 280, 'EAGLE VISION': 280, 'EARMUSIC': 281, 'EARTH ENTERTAINMENT': 282, 'EARTH': 282, 'ECHO BRIDGE ENTERTAINMENT': 283, 'ECHO BRIDGE': 283, 'EDEL GERMANY GMBH': 284, 'EDEL GERMANY': 284, 'EDEL RECORDS': 285, 'EDITION TONFILM': 286, 'EDITIONS MONTPARNASSE': 287, 'EDKO FILMS LTD.': 288, 'EDKO FILMS LTD': 288, 'EDKO FILMS': 288, 'EDKO': 288, "EIN'S M&M CO": 289, 'EINS M&M CO': 289, "EIN'S M&M": 289, 'EINS M&M': 289, 'ELEA-MEDIA': 290, 'ELEA MEDIA': 290, 'ELEA': 290, 'ELECTRIC PICTURE': 291, 'ELECTRIC': 291, 'ELEPHANT FILMS': 292, 'ELEPHANT': 292, 'ELEVATION': 293, 'EMI': 294, 'EMON': 295, 'EMS': 296, 'EMYLIA': 297, 'ENE MEDIA': 298, 'ENE': 298, 'ENTERTAINMENT IN VIDEO': 299, 'ENTERTAINMENT IN': 299, 'ENTERTAINMENT ONE': 300, 'ENTERTAINMENT ONE FILMS CANADA INC.': 301, 'ENTERTAINMENT ONE FILMS CANADA INC': 301, 'ENTERTAINMENT ONE FILMS CANADA': 301, 'ENTERTAINMENT ONE CANADA INC': 301, 
            'ENTERTAINMENT ONE CANADA': 301, 'ENTERTAINMENTONE': 302, 'EONE': 303, 'EOS': 304, 'EPIC PICTURES': 305, 'EPIC': 305, 'EPIC RECORDS': 306, 'ERATO': 307, 'EROS': 308, 'ESC EDITIONS': 309, 'ESCAPI MEDIA BV': 310, 'ESOTERIC RECORDINGS': 311, 'ESPN FILMS': 312, 'EUREKA ENTERTAINMENT': 313, 'EUREKA': 313, 'EURO PICTURES': 314, 'EURO VIDEO': 315, 'EUROARTS': 316, 'EUROPA FILMES': 317, 'EUROPA': 317, 'EUROPACORP': 318, 'EUROZOOM': 319, 'EXCEL': 320, 'EXPLOSIVE MEDIA': 321, 'EXPLOSIVE': 321, 'EXTRALUCID FILMS': 322, 'EXTRALUCID': 322, 'EYE SEE MOVIES': 323, 'EYE SEE': 323, 'EYK MEDIA': 324, 'EYK': 324, 'FABULOUS FILMS': 325, 'FABULOUS': 325, 'FACTORIS FILMS': 326, 'FACTORIS': 326, 'FARAO RECORDS': 327, 'FARBFILM HOME ENTERTAINMENT': 328, 'FARBFILM ENTERTAINMENT': 328, 'FARBFILM HOME': 328, 'FARBFILM': 328, 'FEELGOOD ENTERTAINMENT': 329, 'FEELGOOD': 329, 'FERNSEHJUWELEN': 330, 'FILM CHEST': 331, 'FILM MEDIA': 332, 'FILM MOVEMENT': 333, 'FILM4': 334, 'FILMART': 335, 'FILMAURO': 336, 'FILMAX': 337, 'FILMCONFECT HOME ENTERTAINMENT': 338, 'FILMCONFECT ENTERTAINMENT': 338, 'FILMCONFECT HOME': 338, 'FILMCONFECT': 338, 'FILMEDIA': 339, 'FILMJUWELEN': 340, 'FILMOTEKA NARODAWA': 341, 'FILMRISE': 342, 'FINAL CUT ENTERTAINMENT': 343, 'FINAL CUT': 343, 'FIREHOUSE 12 RECORDS': 344, 'FIREHOUSE 12': 344, 'FIRST INTERNATIONAL PRODUCTION': 345, 'FIRST INTERNATIONAL': 345, 'FIRST LOOK STUDIOS': 346, 'FIRST LOOK': 346, 'FLAGMAN TRADE': 347, 'FLASHSTAR FILMES': 348, 'FLASHSTAR': 348, 'FLICKER ALLEY': 349, 'FNC ADD CULTURE': 350, 'FOCUS FILMES': 351, 'FOCUS': 351, 'FOKUS MEDIA': 352, 'FOKUSA': 352, 'FOX PATHE EUROPA': 353, 'FOX PATHE': 353, 'FOX EUROPA': 353, 'FOX/MGM': 354, 'FOX MGM': 354, 'MGM': 354, 'MGM/FOX': 354, 'FOX': 354, 'FPE': 355, 'FRANCE TÉLÉVISIONS DISTRIBUTION': 356, 'FRANCE TELEVISIONS DISTRIBUTION': 356, 'FRANCE TELEVISIONS': 356, 'FRANCE': 356, 'FREE DOLPHIN ENTERTAINMENT': 357, 'FREE DOLPHIN': 357, 'FREESTYLE DIGITAL MEDIA': 358, 'FREESTYLE DIGITAL': 358, 'FREESTYLE': 358, 'FREMANTLE HOME ENTERTAINMENT': 359, 'FREMANTLE ENTERTAINMENT': 359, 'FREMANTLE HOME': 359, 'FREMANTL': 359, 'FRENETIC FILMS': 360, 'FRENETIC': 360, 'FRONTIER WORKS': 361, 'FRONTIER': 361, 'FRONTIERS MUSIC': 362, 'FRONTIERS RECORDS': 363, 'FS FILM OY': 364, 'FS FILM': 
            364, 'FULL MOON FEATURES': 365, 'FULL MOON': 365, 'FUN CITY EDITIONS': 366, 'FUN CITY': 366, 'FUNIMATION ENTERTAINMENT': 367, 'FUNIMATION': 367, 'FUSION': 368, 'FUTUREFILM': 369, 'G2 PICTURES': 370, 'G2': 370, 'GAGA COMMUNICATIONS': 371, 'GAGA': 371, 'GAIAM': 372, 'GALAPAGOS': 373, 'GAMMA HOME ENTERTAINMENT': 374, 'GAMMA ENTERTAINMENT': 374, 'GAMMA HOME': 374, 'GAMMA': 374, 'GARAGEHOUSE PICTURES': 375, 'GARAGEHOUSE': 375, 'GARAGEPLAY (車庫娛樂)': 376, '車庫娛樂': 376, 'GARAGEPLAY (Che Ku Yu Le )': 376, 'GARAGEPLAY': 376, 'Che Ku Yu Le': 376, 'GAUMONT': 377, 'GEFFEN': 378, 'GENEON ENTERTAINMENT': 379, 'GENEON': 379, 'GENEON UNIVERSAL ENTERTAINMENT': 380, 'GENERAL VIDEO RECORDING': 381, 'GLASS DOLL FILMS': 382, 'GLASS DOLL': 382, 'GLOBE MUSIC MEDIA': 383, 'GLOBE MUSIC': 383, 'GLOBE MEDIA': 383, 'GLOBE': 383, 'GO ENTERTAIN': 384, 'GO': 384, 'GOLDEN HARVEST': 385, 'GOOD!MOVIES': 386, 
            'GOOD! MOVIES': 386, 'GOOD MOVIES': 386, 'GRAPEVINE VIDEO': 387, 'GRAPEVINE': 387, 'GRASSHOPPER FILM': 388, 'GRASSHOPPER FILMS': 388, 'GRASSHOPPER': 388, 'GRAVITAS VENTURES': 389, 'GRAVITAS': 389, 'GREAT MOVIES': 390, 'GREAT': 390, 
            'GREEN APPLE ENTERTAINMENT': 391, 'GREEN ENTERTAINMENT': 391, 'GREEN APPLE': 391, 'GREEN': 391, 'GREENNARAE MEDIA': 392, 'GREENNARAE': 392, 'GRINDHOUSE RELEASING': 393, 'GRINDHOUSE': 393, 'GRIND HOUSE': 393, 'GRYPHON ENTERTAINMENT': 394, 'GRYPHON': 394, 'GUNPOWDER & SKY': 395, 'GUNPOWDER AND SKY': 395, 'GUNPOWDER SKY': 395, 'GUNPOWDER + SKY': 395, 'GUNPOWDER': 395, 'HANABEE ENTERTAINMENT': 396, 'HANABEE': 396, 'HANNOVER HOUSE': 397, 'HANNOVER': 397, 'HANSESOUND': 398, 'HANSE SOUND': 398, 'HANSE': 398, 'HAPPINET': 399, 'HARMONIA MUNDI': 400, 'HARMONIA': 400, 'HBO': 401, 'HDC': 402, 'HEC': 403, 'HELL & BACK RECORDINGS': 404, 'HELL AND BACK RECORDINGS': 404, 'HELL & BACK': 404, 'HELL AND BACK': 404, "HEN'S TOOTH VIDEO": 405, 'HENS TOOTH VIDEO': 405, "HEN'S TOOTH": 405, 'HENS TOOTH': 405, 'HIGH FLIERS': 406, 'HIGHLIGHT': 407, 'HILLSONG': 408, 'HISTORY CHANNEL': 409, 'HISTORY': 409, 'HK VIDÉO': 410, 'HK VIDEO': 410, 'HK': 410, 'HMH HAMBURGER MEDIEN HAUS': 411, 'HAMBURGER MEDIEN HAUS': 411, 'HMH HAMBURGER MEDIEN': 411, 'HMH HAMBURGER': 411, 'HMH': 411, 'HOLLYWOOD CLASSIC ENTERTAINMENT': 412, 'HOLLYWOOD CLASSIC': 412, 'HOLLYWOOD PICTURES': 413, 'HOLLYWOOD': 413, 'HOPSCOTCH ENTERTAINMENT': 414, 'HOPSCOTCH': 414, 'HPM': 415, 'HÄNNSLER CLASSIC': 416, 'HANNSLER CLASSIC': 416, 'HANNSLER': 416, 'I-CATCHER': 417, 'I CATCHER': 417, 'ICATCHER': 417, 'I-ON NEW MEDIA': 418, 'I ON NEW MEDIA': 418, 'ION NEW MEDIA': 418, 'ION MEDIA': 418, 'I-ON': 418, 'ION': 418, 'IAN PRODUCTIONS': 419, 'IAN': 419, 'ICESTORM': 420, 'ICON FILM DISTRIBUTION': 421, 'ICON DISTRIBUTION': 421, 'ICON FILM': 421, 'ICON': 421, 'IDEALE AUDIENCE': 422, 'IDEALE': 422, 'IFC FILMS': 423, 'IFC': 423, 'IFILM': 424, 'ILLUSIONS UNLTD.': 425, 'ILLUSIONS UNLTD': 425, 'ILLUSIONS': 425, 'IMAGE ENTERTAINMENT': 426, 'IMAGE': 426, 
            'IMAGEM FILMES': 427, 'IMAGEM': 427, 'IMOVISION': 428, 'IMPERIAL CINEPIX': 429, 'IMPRINT': 430, 'IMPULS HOME ENTERTAINMENT': 431, 'IMPULS ENTERTAINMENT': 431, 'IMPULS HOME': 431, 'IMPULS': 431, 'IN-AKUSTIK': 432, 'IN AKUSTIK': 432, 'INAKUSTIK': 432, 'INCEPTION MEDIA GROUP': 433, 'INCEPTION MEDIA': 433, 'INCEPTION GROUP': 433, 'INCEPTION': 433, 'INDEPENDENT': 434, 'INDICAN': 435, 'INDIE RIGHTS': 436, 'INDIE': 436, 'INDIGO': 437, 'INFO': 438, 'INJOINGAN': 439, 'INKED PICTURES': 440, 'INKED': 440, 'INSIDE OUT MUSIC': 441, 'INSIDE MUSIC': 441, 'INSIDE OUT': 441, 'INSIDE': 441, 'INTERCOM': 442, 'INTERCONTINENTAL VIDEO': 443, 'INTERCONTINENTAL': 443, 'INTERGROOVE': 444, 
            'INTERSCOPE': 445, 'INVINCIBLE PICTURES': 446, 'INVINCIBLE': 446, 'ISLAND/MERCURY': 447, 'ISLAND MERCURY': 447, 'ISLANDMERCURY': 447, 'ISLAND & MERCURY': 447, 'ISLAND AND MERCURY': 447, 'ISLAND': 447, 'ITN': 448, 'ITV DVD': 449, 'ITV': 449, 'IVC': 450, 'IVE ENTERTAINMENT': 451, 'IVE': 451, 'J&R ADVENTURES': 452, 'J&R': 452, 'JR': 452, 'JAKOB': 453, 'JONU MEDIA': 454, 'JONU': 454, 'JRB PRODUCTIONS': 455, 'JRB': 455, 'JUST BRIDGE ENTERTAINMENT': 456, 'JUST BRIDGE': 456, 'JUST ENTERTAINMENT': 456, 'JUST': 456, 'KABOOM ENTERTAINMENT': 457, 'KABOOM': 457, 'KADOKAWA ENTERTAINMENT': 458, 'KADOKAWA': 458, 'KAIROS': 459, 'KALEIDOSCOPE ENTERTAINMENT': 460, 'KALEIDOSCOPE': 460, 'KAM & RONSON ENTERPRISES': 461, 'KAM & RONSON': 461, 'KAM&RONSON ENTERPRISES': 461, 'KAM&RONSON': 461, 'KAM AND RONSON ENTERPRISES': 461, 'KAM AND RONSON': 461, 'KANA HOME VIDEO': 462, 'KARMA FILMS': 463, 'KARMA': 463, 'KATZENBERGER': 464, 'KAZE': 465, 'KBS MEDIA': 466, 'KBS': 466, 'KD MEDIA': 467, 'KD': 467, 'KING MEDIA': 468, 'KING': 468, 'KING RECORDS': 469, 'KINO LORBER': 470, 'KINO': 470, 'KINO SWIAT': 471, 'KINOKUNIYA': 472, 'KINOWELT HOME ENTERTAINMENT/DVD': 473, 'KINOWELT HOME ENTERTAINMENT': 473, 'KINOWELT ENTERTAINMENT': 473, 'KINOWELT HOME DVD': 473, 'KINOWELT ENTERTAINMENT/DVD': 473, 'KINOWELT DVD': 473, 'KINOWELT': 473, 'KIT PARKER FILMS': 474, 'KIT PARKER': 474, 'KITTY MEDIA': 475, 'KNM HOME ENTERTAINMENT': 476, 'KNM ENTERTAINMENT': 476, 'KNM HOME': 476, 'KNM': 476, 'KOBA FILMS': 477, 'KOBA': 477, 'KOCH ENTERTAINMENT': 478, 'KOCH MEDIA': 479, 'KOCH': 479, 'KRAKEN RELEASING': 480, 'KRAKEN': 480, 'KSCOPE': 481, 'KSM': 482, 'KULTUR': 483, "L'ATELIER D'IMAGES": 484, "LATELIER D'IMAGES": 484, "L'ATELIER DIMAGES": 484, 'LATELIER DIMAGES': 484, "L ATELIER D'IMAGES": 484, "L'ATELIER D IMAGES": 484, 
            'L ATELIER D IMAGES': 484, "L'ATELIER": 484, 'L ATELIER': 484, 'LATELIER': 484, 'LA AVENTURA AUDIOVISUAL': 485, 'LA AVENTURA': 485, 'LACE GROUP': 486, 'LACE': 486, 'LASER PARADISE': 487, 'LAYONS': 488, 'LCJ EDITIONS': 489, 'LCJ': 489, 'LE CHAT QUI FUME': 490, 'LE PACTE': 491, 'LEDICK FILMHANDEL': 492, 'LEGEND': 493, 'LEOMARK STUDIOS': 494, 'LEOMARK': 494, 'LEONINE FILMS': 495, 'LEONINE': 495, 'LICHTUNG MEDIA LTD': 496, 'LICHTUNG LTD': 496, 'LICHTUNG MEDIA LTD.': 496, 'LICHTUNG LTD.': 496, 'LICHTUNG MEDIA': 496, 'LICHTUNG': 496, 'LIGHTHOUSE HOME ENTERTAINMENT': 497, 'LIGHTHOUSE ENTERTAINMENT': 497, 'LIGHTHOUSE HOME': 497, 'LIGHTHOUSE': 497, 'LIGHTYEAR': 498, 'LIONSGATE FILMS': 499, 'LIONSGATE': 499, 'LIZARD CINEMA TRADE': 500, 'LLAMENTOL': 501, 'LOBSTER FILMS': 502, 'LOBSTER': 502, 'LOGON': 503, 'LORBER FILMS': 504, 'LORBER': 504, 'LOS BANDITOS FILMS': 505, 'LOS BANDITOS': 505, 'LOUD & PROUD RECORDS': 506, 'LOUD AND PROUD RECORDS': 506, 'LOUD & PROUD': 506, 'LOUD AND PROUD': 506, 'LSO LIVE': 507, 'LUCASFILM': 508, 'LUCKY RED': 509, 'LUMIÈRE HOME ENTERTAINMENT': 510, 'LUMIERE HOME ENTERTAINMENT': 510, 'LUMIERE ENTERTAINMENT': 510, 'LUMIERE HOME': 510, 'LUMIERE': 510, 'M6 VIDEO': 511, 'M6': 511, 'MAD DIMENSION': 512, 'MADMAN ENTERTAINMENT': 513, 'MADMAN': 513, 'MAGIC BOX': 514, 'MAGIC PLAY': 515, 'MAGNA HOME ENTERTAINMENT': 516, 'MAGNA ENTERTAINMENT': 516, 'MAGNA HOME': 516, 'MAGNA': 516, 'MAGNOLIA PICTURES': 517, 'MAGNOLIA': 517, 'MAIDEN JAPAN': 518, 'MAIDEN': 518, 'MAJENG MEDIA': 519, 'MAJENG': 519, 'MAJESTIC HOME ENTERTAINMENT': 520, 'MAJESTIC ENTERTAINMENT': 520, 'MAJESTIC HOME': 520, 'MAJESTIC': 520, 'MANGA HOME ENTERTAINMENT': 521, 'MANGA ENTERTAINMENT': 521, 'MANGA HOME': 521, 'MANGA': 521, 'MANTA LAB': 522, 'MAPLE STUDIOS': 523, 'MAPLE': 523, 'MARCO POLO PRODUCTION': 
            524, 'MARCO POLO': 524, 'MARIINSKY': 525, 'MARVEL STUDIOS': 526, 'MARVEL': 526, 'MASCOT RECORDS': 527, 'MASCOT': 527, 'MASSACRE VIDEO': 528, 'MASSACRE': 528, 'MATCHBOX': 529, 'MATRIX D': 530, 'MAXAM': 531, 'MAYA HOME ENTERTAINMENT': 532, 'MAYA ENTERTAINMENT': 532, 'MAYA HOME': 532, 'MAYAT': 532, 'MDG': 533, 'MEDIA BLASTERS': 534, 'MEDIA FACTORY': 535, 'MEDIA TARGET DISTRIBUTION': 536, 'MEDIA TARGET': 536, 'MEDIAINVISION': 537, 'MEDIATOON': 538, 'MEDIATRES ESTUDIO': 539, 'MEDIATRES STUDIO': 539, 'MEDIATRES': 539, 'MEDICI ARTS': 540, 'MEDICI CLASSICS': 541, 'MEDIUMRARE ENTERTAINMENT': 542, 'MEDIUMRARE': 542, 'MEDUSA': 543, 'MEGASTAR': 544, 'MEI AH': 545, 'MELI MÉDIAS': 546, 'MELI MEDIAS': 546, 'MEMENTO FILMS': 547, 'MEMENTO': 547, 'MENEMSHA FILMS': 548, 'MENEMSHA': 548, 'MERCURY': 549, 'MERCURY STUDIOS': 550, 'MERGE SOFT PRODUCTIONS': 551, 'MERGE PRODUCTIONS': 551, 'MERGE SOFT': 551, 'MERGE': 551, 'METAL BLADE RECORDS': 552, 'METAL BLADE': 552, 'METEOR': 553, 'METRO-GOLDWYN-MAYER': 554, 'METRO GOLDWYN MAYER': 554, 'METROGOLDWYNMAYER': 554, 'METRODOME VIDEO': 555, 'METRODOME': 555, 'METROPOLITAN': 556, 'MFA+': 
            557, 'MFA': 557, 'MIG FILMGROUP': 558, 'MIG': 558, 'MILESTONE': 559, 'MILL CREEK ENTERTAINMENT': 560, 'MILL CREEK': 560, 'MILLENNIUM MEDIA': 561, 'MILLENNIUM': 561, 'MIRAGE ENTERTAINMENT': 562, 'MIRAGE': 562, 'MIRAMAX': 563, 
            'MISTERIYA ZVUKA': 564, 'MK2': 565, 'MODE RECORDS': 566, 'MODE': 566, 'MOMENTUM PICTURES': 567, 'MONDO HOME ENTERTAINMENT': 568, 'MONDO ENTERTAINMENT': 568, 'MONDO HOME': 568, 'MONDO MACABRO': 569, 'MONGREL MEDIA': 570, 'MONOLIT': 571, 'MONOLITH VIDEO': 572, 'MONOLITH': 572, 'MONSTER PICTURES': 573, 'MONSTER': 573, 'MONTEREY VIDEO': 574, 'MONTEREY': 574, 'MONUMENT RELEASING': 575, 'MONUMENT': 575, 'MORNINGSTAR': 576, 'MORNING STAR': 576, 'MOSERBAER': 577, 'MOVIEMAX': 578, 'MOVINSIDE': 579, 'MPI MEDIA GROUP': 580, 'MPI MEDIA': 580, 'MPI': 580, 'MR. BONGO FILMS': 581, 'MR BONGO FILMS': 581, 'MR BONGO': 581, 'MRG (MERIDIAN)': 582, 'MRG MERIDIAN': 582, 'MRG': 582, 'MERIDIAN': 582, 'MUBI': 583, 'MUG SHOT PRODUCTIONS': 584, 'MUG SHOT': 584, 'MULTIMUSIC': 585, 'MULTI-MUSIC': 585, 'MULTI MUSIC': 585, 'MUSE': 586, 'MUSIC BOX FILMS': 587, 'MUSIC BOX': 587, 'MUSICBOX': 587, 'MUSIC BROKERS': 588, 'MUSIC THEORIES': 589, 'MUSIC VIDEO DISTRIBUTORS': 590, 'MUSIC VIDEO': 590, 'MUSTANG ENTERTAINMENT': 591, 'MUSTANG': 591, 'MVD VISUAL': 592, 'MVD': 592, 'MVD/VSC': 593, 'MVL': 594, 'MVM ENTERTAINMENT': 595, 'MVM': 595, 'MYNDFORM': 596, 'MYSTIC NIGHT PICTURES': 597, 'MYSTIC NIGHT': 597, 'NAMELESS MEDIA': 598, 'NAMELESS': 598, 'NAPALM RECORDS': 599, 'NAPALM': 599, 'NATIONAL ENTERTAINMENT MEDIA': 600, 'NATIONAL ENTERTAINMENT': 600, 'NATIONAL MEDIA': 600, 'NATIONAL FILM ARCHIVE': 601, 'NATIONAL ARCHIVE': 601, 'NATIONAL FILM': 601, 'NATIONAL GEOGRAPHIC': 602, 'NAT GEO TV': 602, 'NAT GEO': 602, 'NGO': 602, 'NAXOS': 603, 'NBCUNIVERSAL ENTERTAINMENT JAPAN': 604, 'NBC UNIVERSAL ENTERTAINMENT JAPAN': 604, 'NBCUNIVERSAL JAPAN': 604, 'NBC UNIVERSAL JAPAN': 604, 'NBC JAPAN': 604, 'NBO ENTERTAINMENT': 605, 'NBO': 605, 'NEOS': 606, 'NETFLIX': 607, 'NETWORK': 608, 'NEW BLOOD': 609, 'NEW DISC': 610, 'NEW KSM': 611, 'NEW LINE CINEMA': 612, 'NEW LINE': 612, 'NEW MOVIE TRADING CO. LTD': 613, 'NEW MOVIE TRADING CO LTD': 613, 'NEW MOVIE TRADING CO': 613, 'NEW MOVIE TRADING': 613, 'NEW WAVE FILMS': 614, 'NEW WAVE': 614, 'NFI': 615, 
            'NHK': 616, 'NIPPONART': 617, 'NIS AMERICA': 618, 'NJUTAFILMS': 619, 'NOBLE ENTERTAINMENT': 620, 'NOBLE': 620, 'NORDISK FILM': 621, 'NORDISK': 621, 'NORSK FILM': 622, 'NORSK': 622, 'NORTH AMERICAN MOTION PICTURES': 623, 'NOS AUDIOVISUAIS': 624, 'NOTORIOUS PICTURES': 625, 'NOTORIOUS': 625, 'NOVA MEDIA': 626, 'NOVA': 626, 'NOVA SALES AND DISTRIBUTION': 627, 'NOVA SALES & DISTRIBUTION': 627, 'NSM': 628, 'NSM RECORDS': 629, 'NUCLEAR BLAST': 630, 'NUCLEUS FILMS': 631, 'NUCLEUS': 631, 'OBERLIN MUSIC': 632, 'OBERLIN': 632, 'OBRAS-PRIMAS DO CINEMA': 633, 'OBRAS PRIMAS DO CINEMA': 633, 'OBRASPRIMAS DO CINEMA': 633, 'OBRAS-PRIMAS CINEMA': 633, 'OBRAS PRIMAS CINEMA': 633, 'OBRASPRIMAS CINEMA': 633, 'OBRAS-PRIMAS': 633, 'OBRAS PRIMAS': 633, 'OBRASPRIMAS': 633, 'ODEON': 634, 'OFDB FILMWORKS': 635, 'OFDB': 635, 'OLIVE FILMS': 636, 'OLIVE': 636, 'ONDINE': 637, 'ONSCREEN FILMS': 638, 'ONSCREEN': 638, 'OPENING DISTRIBUTION': 639, 'OPERA AUSTRALIA': 640, 'OPTIMUM HOME ENTERTAINMENT': 641, 'OPTIMUM ENTERTAINMENT': 641, 'OPTIMUM HOME': 641, 'OPTIMUM': 641, 'OPUS ARTE': 642, 'ORANGE STUDIO': 643, 'ORANGE': 643, 'ORLANDO EASTWOOD FILMS': 644, 'ORLANDO FILMS': 644, 'ORLANDO EASTWOOD': 644, 'ORLANDO': 644, 'ORUSTAK PICTURES': 645, 'ORUSTAK': 645, 'OSCILLOSCOPE PICTURES': 646, 'OSCILLOSCOPE': 646, 'OUTPLAY': 647, 'PALISADES TARTAN': 648, 'PAN VISION': 649, 'PANVISION': 649, 'PANAMINT CINEMA': 650, 'PANAMINT': 650, 'PANDASTORM ENTERTAINMENT': 651, 'PANDA STORM ENTERTAINMENT': 651, 'PANDASTORM': 651, 'PANDA STORM': 651, 'PANDORA FILM': 652, 'PANDORA': 652, 'PANEGYRIC': 653, 'PANORAMA': 654, 'PARADE DECK FILMS': 655, 'PARADE DECK': 655, 'PARADISE': 656, 'PARADISO FILMS': 657, 'PARADOX': 658, 'PARAMOUNT PICTURES': 659, 'PARAMOUNT': 659, 'PARIS FILMES': 660, 'PARIS FILMS': 660, 'PARIS': 660, 'PARK CIRCUS': 661, 'PARLOPHONE': 662, 'PASSION RIVER': 663, 'PATHE DISTRIBUTION': 664, 'PATHE': 664, 'PBS': 665, 'PEACE ARCH TRINITY': 666, 'PECCADILLO PICTURES': 667, 'PEPPERMINT': 668, 'PHASE 4 FILMS': 669, 'PHASE 4': 669, 'PHILHARMONIA BAROQUE': 670, 'PICTURE HOUSE ENTERTAINMENT': 671, 'PICTURE ENTERTAINMENT': 671, 'PICTURE HOUSE': 671, 'PICTURE': 671, 'PIDAX': 672, 'PINK FLOYD RECORDS': 673, 'PINK FLOYD': 673, 'PINNACLE FILMS': 674, 'PINNACLE': 674, 'PLAIN': 675, 'PLATFORM ENTERTAINMENT LIMITED': 676, 'PLATFORM ENTERTAINMENT LTD': 676, 'PLATFORM ENTERTAINMENT LTD.': 676, 'PLATFORM ENTERTAINMENT': 676, 'PLATFORM': 676, 'PLAYARTE': 677, 'PLG UK CLASSICS': 678, 'PLG UK': 
            678, 'PLG': 678, 'POLYBAND & TOPPIC VIDEO/WVG': 679, 'POLYBAND AND TOPPIC VIDEO/WVG': 679, 'POLYBAND & TOPPIC VIDEO WVG': 679, 'POLYBAND & TOPPIC VIDEO AND WVG': 679, 'POLYBAND & TOPPIC VIDEO & WVG': 679, 'POLYBAND AND TOPPIC VIDEO WVG': 679, 'POLYBAND AND TOPPIC VIDEO AND WVG': 679, 'POLYBAND AND TOPPIC VIDEO & WVG': 679, 'POLYBAND & TOPPIC VIDEO': 679, 'POLYBAND AND TOPPIC VIDEO': 679, 'POLYBAND & TOPPIC': 679, 'POLYBAND AND TOPPIC': 679, 'POLYBAND': 679, 'WVG': 679, 'POLYDOR': 680, 'PONY': 681, 'PONY CANYON': 682, 'POTEMKINE': 683, 'POWERHOUSE FILMS': 684, 'POWERHOUSE': 684, 'POWERSTATIOM': 685, 'PRIDE & JOY': 686, 'PRIDE AND JOY': 686, 'PRINZ MEDIA': 687, 'PRINZ': 687, 'PRIS AUDIOVISUAIS': 688, 'PRO VIDEO': 689, 'PRO-VIDEO': 689, 'PRO-MOTION': 690, 'PRO MOTION': 690, 'PROD. JRB': 691, 'PROD JRB': 691, 'PRODISC': 692, 'PROKINO': 693, 'PROVOGUE RECORDS': 694, 'PROVOGUE': 694, 'PROWARE': 695, 'PULP VIDEO': 696, 'PULP': 696, 'PULSE VIDEO': 697, 'PULSE': 697, 'PURE AUDIO RECORDINGS': 698, 'PURE AUDIO': 698, 'PURE FLIX ENTERTAINMENT': 699, 'PURE FLIX': 699, 'PURE ENTERTAINMENT': 699, 'PYRAMIDE VIDEO': 700, 'PYRAMIDE': 700, 'QUALITY FILMS': 701, 'QUALITY': 701, 'QUARTO VALLEY RECORDS': 702, 'QUARTO VALLEY': 702, 'QUESTAR': 703, 'R SQUARED FILMS': 704, 'R SQUARED': 704, 'RAPID EYE MOVIES': 705, 'RAPID EYE': 705, 'RARO VIDEO': 706, 'RARO': 706, 'RAROVIDEO U.S.': 707, 'RAROVIDEO US': 707, 'RARO VIDEO US': 707, 'RARO VIDEO U.S.': 707, 'RARO U.S.': 707, 'RARO US': 707, 'RAVEN BANNER RELEASING': 708, 'RAVEN BANNER': 708, 'RAVEN': 708, 'RAZOR DIGITAL ENTERTAINMENT': 709, 'RAZOR DIGITAL': 709, 'RCA': 710, 'RCO LIVE': 711, 'RCO': 711, 'RCV': 712, 'REAL GONE MUSIC': 713, 'REAL GONE': 713, 'REANIMEDIA': 714, 'REANI MEDIA': 714, 'REDEMPTION': 715, 'REEL': 716, 'RELIANCE HOME VIDEO & GAMES': 717, 'RELIANCE HOME VIDEO AND GAMES': 717, 'RELIANCE HOME VIDEO': 717, 'RELIANCE VIDEO': 717, 'RELIANCE HOME': 717, 'RELIANCE': 717, 'REM CULTURE': 718, 'REMAIN IN LIGHT': 719, 'REPRISE': 720, 'RESEN': 721, 'RETROMEDIA': 722, 'REVELATION FILMS LTD.': 723, 'REVELATION FILMS LTD': 723, 'REVELATION FILMS': 723, 'REVELATION LTD.': 723, 'REVELATION LTD': 723, 'REVELATION': 723, 'REVOLVER ENTERTAINMENT': 724, 'REVOLVER': 724, 'RHINO MUSIC': 725, 'RHINO': 725, 'RHV': 726, 'RIGHT STUF': 727, 'RIMINI EDITIONS': 728, 'RISING SUN MEDIA': 729, 'RLJ ENTERTAINMENT': 730, 'RLJ': 730, 'ROADRUNNER RECORDS': 731, 'ROADSHOW ENTERTAINMENT': 732, 'ROADSHOW': 732, 'RONE': 733, 'RONIN FLIX': 734, 'ROTANA HOME ENTERTAINMENT': 735, 'ROTANA ENTERTAINMENT': 735, 'ROTANA HOME': 735, 'ROTANA': 735, 'ROUGH TRADE': 736, 'ROUNDER': 737, 'SAFFRON HILL FILMS': 738, 'SAFFRON HILL': 738, 'SAFFRON': 738, 'SAMUEL GOLDWYN FILMS': 739, 'SAMUEL GOLDWYN': 739, 'SAN FRANCISCO SYMPHONY': 740, 'SANDREW METRONOME': 741, 'SAPHRANE': 742, 'SAVOR': 743, 'SCANBOX ENTERTAINMENT': 744, 'SCANBOX': 744, 'SCENIC LABS': 745, 'SCHRÖDERMEDIA': 746, 'SCHRODERMEDIA': 746, 'SCHRODER MEDIA': 746, 'SCORPION RELEASING': 747, 'SCORPION': 747, 'SCREAM TRACKERM RELEASING': 748, 'SCREAM TRACKERM': 748, 'SCREEN MEDIA': 749, 'SCREEN': 749, 'SCREENBOUND PICTURES': 750, 'SCREENBOUND': 750, 'SCREENWAVE MEDIA': 751, 'SCREENWAVE': 751, 'SECOND RUN': 752, 'SECOND SIGHT': 753, 'SEEDSMAN GROUP': 754, 'SELECT VIDEO': 755, 'SELECTA VISION': 756, 'SENATOR': 757, 'SENTAI FILMWORKS': 758, 'SENTAI': 758, 'SEVEN7': 759, 'SEVERIN FILMS': 760, 'SEVERIN': 760, 'SEVILLE': 761, 'SEYONS ENTERTAINMENT': 762, 'SEYONS': 762, 'SF STUDIOS': 763, 'SGL ENTERTAINMENT': 764, 'SGL': 764, 'SHAMELESS': 765, 'SHAMROCK MEDIA': 766, 'SHAMROCK': 766, 'SHANGHAI EPIC MUSIC ENTERTAINMENT': 767, 'SHANGHAI EPIC ENTERTAINMENT': 767, 'SHANGHAI EPIC MUSIC': 767, 'SHANGHAI MUSIC ENTERTAINMENT': 767, 'SHANGHAI ENTERTAINMENT': 767, 'SHANGHAI MUSIC': 767, 'SHANGHAI': 767, 'SHEMAROO': 768, 'SHOCHIKU': 769, 'SHOCK': 770, 'SHOGAKU KAN': 771, 'SHOUT FACTORY': 772, 'SHOUT! FACTORY': 772, 'SHOUT': 772, 'SHOUT!': 772, 'SHOWBOX': 773, 'SHOWTIME ENTERTAINMENT': 774, 'SHOWTIME': 774, 'SHRIEK SHOW': 775, 'SHUDDER': 776, 'SIDONIS': 777, 'SIDONIS CALYSTA': 778, 'SIGNAL ONE ENTERTAINMENT': 779, 'SIGNAL ONE': 779, 'SIGNATURE ENTERTAINMENT': 780, 'SIGNATURE': 780, 'SILVER VISION': 781, 'SINISTER FILM': 782, 'SINISTER': 782, 'SIREN VISUAL ENTERTAINMENT': 783, 'SIREN VISUAL': 783, 'SIREN ENTERTAINMENT': 783, 'SIREN': 783, 'SKANI': 784, 'SKY DIGI': 785, 'SLASHER // VIDEO': 786, 'SLASHER / VIDEO': 786, 'SLASHER VIDEO': 786, 'SLASHER': 786, 'SLOVAK FILM INSTITUTE': 787, 'SLOVAK FILM': 787, 
            'SFI': 787, 'SM LIFE DESIGN GROUP': 788, 'SMOOTH PICTURES': 789, 'SMOOTH': 789, 'SNAPPER MUSIC': 790, 'SNAPPER': 790, 'SODA PICTURES': 791, 'SODA': 791, 'SONO LUMINUS': 792, 'SONY MUSIC': 793, 'SONY PICTURES': 794, 'SONY': 794, 'SONY PICTURES CLASSICS': 795, 'SONY CLASSICS': 795, 'SOUL MEDIA': 796, 'SOUL': 796, 'SOULFOOD MUSIC DISTRIBUTION': 797, 'SOULFOOD DISTRIBUTION': 797, 'SOULFOOD MUSIC': 797, 'SOULFOOD': 797, 'SOYUZ': 798, 'SPECTRUM': 799, 
            'SPENTZOS FILM': 800, 'SPENTZOS': 800, 'SPIRIT ENTERTAINMENT': 801, 'SPIRIT': 801, 'SPIRIT MEDIA GMBH': 802, 'SPIRIT MEDIA': 802, 'SPLENDID ENTERTAINMENT': 803, 'SPLENDID FILM': 804, 'SPO': 805, 'SQUARE ENIX': 806, 'SRI BALAJI VIDEO': 807, 'SRI BALAJI': 807, 'SRI': 807, 'SRI VIDEO': 807, 'SRS CINEMA': 808, 'SRS': 808, 'SSO RECORDINGS': 809, 'SSO': 809, 'ST2 MUSIC': 810, 'ST2': 810, 'STAR MEDIA ENTERTAINMENT': 811, 'STAR ENTERTAINMENT': 811, 'STAR MEDIA': 811, 'STAR': 811, 'STARLIGHT': 812, 'STARZ / ANCHOR BAY': 813, 'STARZ ANCHOR BAY': 813, 'STARZ': 813, 'ANCHOR BAY': 813, 'STER KINEKOR': 814, 'STERLING ENTERTAINMENT': 815, 'STERLING': 815, 'STINGRAY': 816, 'STOCKFISCH RECORDS': 817, 'STOCKFISCH': 817, 'STRAND RELEASING': 818, 'STRAND': 818, 'STUDIO 4K': 819, 'STUDIO CANAL': 820, 'STUDIO GHIBLI': 821, 'GHIBLI': 821, 'STUDIO HAMBURG ENTERPRISES': 822, 'HAMBURG ENTERPRISES': 822, 'STUDIO HAMBURG': 822, 'HAMBURG': 822, 'STUDIO S': 823, 'SUBKULTUR ENTERTAINMENT': 824, 'SUBKULTUR': 824, 'SUEVIA FILMS': 825, 'SUEVIA': 825, 'SUMMIT ENTERTAINMENT': 826, 'SUMMIT': 826, 'SUNFILM ENTERTAINMENT': 827, 'SUNFILM': 827, 'SURROUND RECORDS': 828, 'SURROUND': 828, 'SVENSK FILMINDUSTRI': 829, 'SVENSK': 829, 'SWEN FILMES': 830, 'SWEN FILMS': 830, 'SWEN': 830, 'SYNAPSE FILMS': 831, 'SYNAPSE': 831, 'SYNDICADO': 832, 'SYNERGETIC': 833, 'T- SERIES': 834, 'T-SERIES': 834, 'T SERIES': 834, 'TSERIES': 834, 'T.V.P.': 835, 'TVP': 835, 'TACET RECORDS': 836, 'TACET': 836, 'TAI SENG': 837, 'TAI SHENG': 838, 'TAKEONE': 839, 'TAKESHOBO': 840, 'TAMASA DIFFUSION': 841, 'TC ENTERTAINMENT': 842, 'TC': 842, 'TDK': 843, 'TRACKERM MARKETING': 844, 'TRACKERTRO REAL': 845, 'TEMA DISTRIBUCIONES': 846, 'TEMPE DIGITAL': 847, 'TF1 VIDÉO': 848, 'TF1 VIDEO': 848, 'TF1': 848, 'THE BLU': 849, 'BLU': 849, 'THE ECSTASY OF FILMS': 850, 'THE FILM DETECTIVE': 851, 'FILM DETECTIVE': 851, 'THE JOKERS': 852, 'JOKERS': 852, 'THE ON': 853, 'ON': 853, 'THIMFILM': 854, 'THIM FILM': 854, 'THIM': 854, 'THIRD WINDOW FILMS': 855, 'THIRD WINDOW': 855, '3RD WINDOW FILMS': 855, '3RD WINDOW': 855, 'THUNDERBEAN ANIMATION': 856, 'THUNDERBEAN': 856, 'THUNDERBIRD RELEASING': 857, 'THUNDERBIRD': 857, 'TIBERIUS FILM': 858, 'TIME LIFE': 859, 'TIMELESS MEDIA GROUP': 860, 'TIMELESS MEDIA': 860, 'TIMELESS GROUP': 860, 'TIMELESS': 860, 'TLA RELEASING': 861, 'TLA': 861, 'TOBIS FILM': 862, 'TOBIS': 862, 'TOEI': 863, 'TOHO': 864, 'TOKYO SHOCK': 865, 'TOKYO': 865, 'TONPOOL MEDIEN GMBH': 866, 'TONPOOL MEDIEN': 866, 'TOPICS ENTERTAINMENT': 867, 'TOPICS': 867, 'TOUCHSTONE PICTURES': 868, 'TOUCHSTONE': 868, 'TRANSMISSION FILMS': 869, 'TRANSMISSION': 869, 'TRAVEL VIDEO STORE': 870, 'TRIART': 871, 'TRIGON FILM': 872, 'TRIGON': 872, 'TRINITY HOME ENTERTAINMENT': 873, 'TRINITY ENTERTAINMENT': 873, 'TRINITY HOME': 873, 'TRINITY': 873, 'TRIPICTURES': 874, 'TRI-PICTURES': 874, 'TRI PICTURES': 874, 'TROMA': 875, 'TURBINE MEDIEN': 876, 'TURTLE RECORDS': 877, 'TURTLE': 877, 'TVA FILMS': 878, 'TVA': 878, 'TWILIGHT TIME': 879, 'TWILIGHT': 879, 'TT': 879, 'TWIN CO., LTD.': 880, 'TWIN CO, LTD.': 880, 'TWIN CO., LTD': 880, 'TWIN CO, LTD': 880, 'TWIN CO LTD': 880, 'TWIN LTD': 880, 'TWIN CO.': 880, 'TWIN CO': 880, 'TWIN': 880, 'UCA': 881, 'UDR': 882, 'UEK': 883, 'UFA/DVD': 884, 'UFA DVD': 884, 'UFADVD': 884, 'UGC PH': 885, 'ULTIMATE3DHEAVEN': 886, 'ULTRA': 887, 'UMBRELLA ENTERTAINMENT': 888, 'UMBRELLA': 888, 'UMC': 889, "UNCORK'D ENTERTAINMENT": 890, 'UNCORKD ENTERTAINMENT': 890, 'UNCORK D ENTERTAINMENT': 890, "UNCORK'D": 890, 'UNCORK D': 890, 'UNCORKD': 890, 'UNEARTHED FILMS': 891, 'UNEARTHED': 891, 'UNI DISC': 892, 'UNIMUNDOS': 893, 'UNITEL': 894, 'UNIVERSAL MUSIC': 895, 'UNIVERSAL SONY PICTURES HOME ENTERTAINMENT': 896, 'UNIVERSAL SONY PICTURES ENTERTAINMENT': 896, 'UNIVERSAL SONY PICTURES HOME': 896, 'UNIVERSAL SONY PICTURES': 896, 'UNIVERSAL HOME ENTERTAINMENT': 
            896, 'UNIVERSAL ENTERTAINMENT': 896, 'UNIVERSAL HOME': 896, 'UNIVERSAL STUDIOS': 897, 'UNIVERSAL': 897, 'UNIVERSE LASER & VIDEO CO.': 898, 'UNIVERSE LASER AND VIDEO CO.': 898, 'UNIVERSE LASER & VIDEO CO': 898, 'UNIVERSE LASER AND VIDEO CO': 898, 'UNIVERSE LASER CO.': 898, 'UNIVERSE LASER CO': 898, 'UNIVERSE LASER': 898, 'UNIVERSUM FILM': 899, 'UNIVERSUM': 899, 'UTV': 900, 'VAP': 901, 'VCI': 902, 'VENDETTA FILMS': 903, 'VENDETTA': 903, 'VERSÁTIL HOME VIDEO': 904, 'VERSÁTIL VIDEO': 904, 'VERSÁTIL HOME': 904, 'VERSÁTIL': 904, 'VERSATIL HOME VIDEO': 904, 'VERSATIL VIDEO': 904, 'VERSATIL HOME': 904, 'VERSATIL': 904, 'VERTICAL ENTERTAINMENT': 905, 'VERTICAL': 905, 'VÉRTICE 360º': 906, 'VÉRTICE 360': 906, 'VERTICE 360o': 906, 'VERTICE 360': 906, 'VERTIGO BERLIN': 907, 'VÉRTIGO FILMS': 908, 'VÉRTIGO': 908, 'VERTIGO FILMS': 908, 'VERTIGO': 908, 'VERVE PICTURES': 909, 'VIA VISION ENTERTAINMENT': 910, 'VIA VISION': 910, 'VICOL ENTERTAINMENT': 911, 'VICOL': 911, 'VICOM': 912, 'VICTOR ENTERTAINMENT': 913, 'VICTOR': 913, 'VIDEA CDE': 914, 'VIDEO FILM EXPRESS': 915, 'VIDEO FILM': 915, 'VIDEO EXPRESS': 915, 'VIDEO MUSIC, INC.': 916, 'VIDEO MUSIC, INC': 916, 'VIDEO MUSIC INC.': 916, 'VIDEO MUSIC INC': 916, 'VIDEO MUSIC': 916, 'VIDEO SERVICE CORP.': 917, 'VIDEO SERVICE CORP': 917, 'VIDEO SERVICE': 917, 'VIDEO TRAVEL': 918, 'VIDEOMAX': 919, 'VIDEO MAX': 919, 'VII PILLARS ENTERTAINMENT': 920, 'VII PILLARS': 920, 'VILLAGE FILMS': 921, 'VINEGAR SYNDROME': 922, 'VINEGAR': 922, 'VS': 922, 'VINNY MOVIES': 923, 'VINNY': 923, 'VIRGIL FILMS & ENTERTAINMENT': 924, 'VIRGIL FILMS AND ENTERTAINMENT': 924, 'VIRGIL ENTERTAINMENT': 924, 'VIRGIL FILMS': 924, 'VIRGIL': 924, 'VIRGIN RECORDS': 925, 'VIRGIN': 925, 'VISION FILMS': 926, 'VISION': 926, 'VISUAL ENTERTAINMENT GROUP': 927, 'VISUAL GROUP': 927, 'VISUAL ENTERTAINMENT': 927, 'VISUAL': 927, 'VIVENDI VISUAL ENTERTAINMENT': 928, 'VIVENDI VISUAL': 928, 'VIVENDI': 928, 'VIZ PICTURES': 929, 'VIZ': 929, 'VLMEDIA': 930, 'VL MEDIA': 930, 'VL': 930, 'VOLGA': 931, 'VVS FILMS': 932, 
            'VVS': 932, 'VZ HANDELS GMBH': 933, 'VZ HANDELS': 933, 'WARD RECORDS': 934, 'WARD': 934, 'WARNER BROS.': 935, 'WARNER BROS': 935, 'WARNER ARCHIVE': 935, 'WARNER ARCHIVE COLLECTION': 935, 'WAC': 935, 'WARNER': 935, 'WARNER MUSIC': 936, 'WEA': 937, 'WEINSTEIN COMPANY': 938, 'WEINSTEIN': 938, 'WELL GO USA': 939, 'WELL GO': 939, 'WELTKINO FILMVERLEIH': 940, 'WEST VIDEO': 941, 'WEST': 941, 'WHITE PEARL MOVIES': 942, 'WHITE PEARL': 942, 
            'WICKED-VISION MEDIA': 943, 'WICKED VISION MEDIA': 943, 'WICKEDVISION MEDIA': 943, 'WICKED-VISION': 943, 'WICKED VISION': 943, 'WICKEDVISION': 943, 'WIENERWORLD': 944, 'WILD BUNCH': 945, 'WILD EYE RELEASING': 946, 'WILD EYE': 946, 'WILD SIDE VIDEO': 947, 'WILD SIDE': 947, 'WME': 948, 'WOLFE VIDEO': 949, 'WOLFE': 949, 'WORD ON FIRE': 950, 'WORKS FILM GROUP': 951, 'WORLD WRESTLING': 952, 'WVG MEDIEN': 953, 'WWE STUDIOS': 954, 'WWE': 954, 'X RATED KULT': 955, 'X-RATED KULT': 955, 'X RATED CULT': 955, 'X-RATED CULT': 955, 'X RATED': 955, 'X-RATED': 955, 'XCESS': 956, 'XLRATOR': 957, 'XT VIDEO': 958, 'XT': 958, 'YAMATO VIDEO': 959, 'YAMATO': 959, 'YASH RAJ FILMS': 960, 'YASH RAJS': 960, 'ZEITGEIST FILMS': 961, 'ZEITGEIST': 961, 'ZENITH PICTURES': 962, 'ZENITH': 962, 'ZIMA': 963, 'ZYLO': 964, 'ZYX MUSIC': 965, 'ZYX': 965
        }.get(distributor, 0)
        return distributor_id

    async def unit3d_torrent_info(self, tracker, torrent_url, id):
        tmdb = imdb = tvdb = description = category = infohash = mal = None
        imagelist = []
        params = {'api_token' : self.config['TRACKERS'][tracker].get('api_key', '')}
        url = f"{torrent_url}{id}"
        response = requests.get(url=url, params=params)
        try:
            response = response.json()
            attributes = response['attributes']
            category = attributes.get('category')
            description = attributes.get('description')
            tmdb = attributes.get('tmdb_id')
            tvdb = attributes.get('tvdb_id')
            mal = attributes.get('mal_id')
            imdb = attributes.get('imdb_id')
            infohash = attributes.get('info_hash')
            
            bbcode = BBCODE()
            description, imagelist = bbcode.clean_unit3d_description(description, torrent_url)
            console.print(f"[green]Successfully grabbed description from {tracker}")
        except Exception:
            console.print(traceback.print_exc())
            console.print(f"[yellow]Invalid Response from {tracker} API.")
            

        return tmdb, imdb, tvdb, mal, description, category, infohash, imagelist

    async def parseCookieFile(self, cookiefile):
        """Parse a cookies.txt file and return a dictionary of key value pairs
        compatible with requests."""

        cookies = {}
        with open (cookiefile, 'r') as fp:
            for line in fp:
                if not line.startswith(("# ", "\n", "#\n")):
                    lineFields = re.split(' |\t', line.strip())
                    lineFields = [x for x in lineFields if x != ""]
                    cookies[lineFields[5]] = lineFields[6]
        return cookies



    async def ptgen(self, meta, ptgen_site="", ptgen_retry=3):
        ptgen = ""
        url = 'https://ptgen.zhenzhen.workers.dev'
        if ptgen_site != '':
            url = ptgen_site
        params = {}
        data={}
        #get douban url 
        if int(meta.get('imdb_id', '0')) != 0:
            data['search'] = f"tt{meta['imdb_id']}"
            ptgen = requests.get(url, params=data)
            if ptgen.json()["error"] != None:
                for retry in range(ptgen_retry):
                    try:
                        ptgen = requests.get(url, params=params)
                        if ptgen.json()["error"] is None:
                            break
                    except requests.exceptions.JSONDecodeError:
                        continue
            try:
                params['url'] = ptgen.json()['data'][0]['link'] 
            except Exception:
                console.print("[red]Unable to get data from ptgen using IMDb")
                params['url'] = console.input("[red]Please enter [yellow]Douban[/yellow] link: ")
        else:
            console.print("[red]No IMDb id was found.")
            params['url'] = console.input("[red]Please enter [yellow]Douban[/yellow] link: ")
        try:
            ptgen = requests.get(url, params=params)
            if ptgen.json()["error"] != None:
                for retry in range(ptgen_retry):
                    ptgen = requests.get(url, params=params)
                    if ptgen.json()["error"] is None:
                        break
            ptgen = ptgen.json()
            meta['ptgen'] = ptgen
            with open (f"{meta['base_dir']}/tmp/{meta['uuid']}/meta.json", 'w') as f:
                json.dump(meta, f, indent=4)
                f.close()
            ptgen = ptgen['format']
            if "[/img]" in ptgen:
                ptgen = ptgen.split("[/img]")[1]
            ptgen = f"[img]{meta.get('imdb_info', {}).get('cover', meta.get('cover', ''))}[/img]{ptgen}"
        except Exception:
            console.print_exception()
            console.print(ptgen.text)
            console.print("[bold red]There was an error getting the ptgen \nUploading without ptgen")
            return ""
        return ptgen



    # async def ptgen(self, meta):
    #     ptgen = ""
    #     url = "https://api.iyuu.cn/App.Movie.Ptgen"
    #     params = {}
    #     if int(meta.get('imdb_id', '0')) != 0:
    #         params['url'] = f"tt{meta['imdb_id']}"
    #     else:
    #         console.print("[red]No IMDb id was found.")
    #         params['url'] = console.input(f"[red]Please enter [yellow]Douban[/yellow] link: ")
    #     try:
    #         ptgen = requests.get(url, params=params)
    #         ptgen = ptgen.json()
    #         ptgen = ptgen['data']['format']
    #         if "[/img]" in ptgen:
    #             ptgen = ptgen.split("[/img]")[1]
    #         ptgen = f"[img]{meta.get('imdb_info', {}).get('cover', meta.get('cover', ''))}[/img]{ptgen}"
    #     except:
    #         console.print_exception()
    #         console.print("[bold red]There was an error getting the ptgen")
    #         console.print(ptgen)
    #     return ptgen



    async def filter_dupes(self, dupes, meta):
        if meta['debug']:
            console.log("[cyan]Pre-filtered dupes")
            console.log(dupes)
            
        new_dupes = {}
        for each in dupes:
            if meta.get('sd', 0) == 1:
                remove_set = set()
            else:
                remove_set = set({meta['resolution']})
            search_combos = [
                {
                    'search' : meta['hdr'],
                    'search_for' : {'HDR', 'PQ10'},
                    'update' : {'HDR|PQ10'}
                },
                {
                    'search' : meta['hdr'],
                    'search_for' : {'DV'},
                    'update' : {'DV|DoVi'}
                },
                {
                    'search' : meta['hdr'],
                    'search_not' : {'DV', 'DoVi', 'HDR', 'PQ10'},
                    'update' : {'!(DV)|(DoVi)|(HDR)|(PQ10)'}
                },
                {
                    'search' : str(meta.get('tv_pack', 0)),
                    'search_for' : '1',
                    'update' : {fr"{meta['season']}(?!E\d+)"}
                },
                {
                    'search' : meta['episode'],
                    'search_for' : meta['episode'],
                    'update' : {meta['season'], meta['episode']}
                }
            ]
            search_matches = [
                {
                    'if' : {'REMUX', 'WEBDL', 'WEBRip', 'HDTV'},
                    'in' : meta['type']
                }
            ]
            for s in search_combos:
                if s.get('search_for') not in (None, ''):
                    if any(re.search(x, s['search'], flags=re.IGNORECASE) for x in s['search_for']):
                        remove_set.update(s['update'])
                if s.get('search_not') not in (None, ''):
                    if not any(re.search(x, s['search'], flags=re.IGNORECASE) for x in s['search_not']):
                        remove_set.update(s['update'])
            for sm in search_matches:
                for a in sm['if']:
                    if a in sm['in']:
                        remove_set.add(a)

            search = each.lower().replace('-', '').replace(' ', '').replace('.', '')
            for x in remove_set.copy():
                if "|" in x:
                    look_for = x.split('|')
                    for y in look_for:
                        if y.lower() in search:
                            if x in remove_set:
                                remove_set.remove(x)
                            remove_set.add(y)

            allow = True
            for x in remove_set:
                if not x.startswith("!"):
                    if not re.search(x, search, flags=re.I):
                        allow = False
                else:
                    if re.search(x.replace("!", "", 1), search, flags=re.I) not in (None, False):
                        allow = False
            if allow and each not in new_dupes:
                #new_dupes.append(each)
                new_dupes[each] = dupes[each]
        return new_dupes

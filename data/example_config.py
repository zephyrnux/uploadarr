config = {
    'version': '0.4.1',

    "DEFAULT" : {
    
        # ------ READ THIS ------
        # Any lines starting with the # symbol are commented and will not be used.
        # If you change any of these options, remove the #
        # -----------------------

        "tmdb_api" : "TMDB_API_KEY",
        "imgbb_api" : "imgbb_API_KEY",
        "ptpimg_api" : "ptpimg_API_KEY",
        "lensdump_api" : "lensdump_API_KEY",

        # Order of image hosts, and backup image hosts
        "img_host_1": "imgbb",
        "img_host_2": "ptpimg",
        "img_host_3": "imgbox",
	"img_host_4": "pixhost",
        "img_host_5": "lensdump",

        "screens" : "6",
        "img_size" : "500",  #Size in Description [img=350]
        "optimize_images" : True,  # Lossless PNG Compression (True/False)

        "add_trailer" : True, # Adds Movie Trailer (Skips TV as season specifier not supported)

        "use_global_sigs": True, # If False it will search for your tracker signature or anon_signature        
        "global_sig": f"\n[center][size=6][url=https://github.com/z-ink/Upload-Assistant]Upload Assistant(CvT Mod v0.4)[/url][/size][/center]", 
        "global_anon_sig": f"\n[center][size=6]we are anonymous[/size][/center]",
        # The name of your default torrent client, set in the torrent client sections below
        "default_torrent_client" : "Client1",

        # Play the bell sound effect when asking for confirmation
        "sfx_on_prompt" : True,

    },

    "TRACKERS" : {
        # Which trackers do you want to upload to? Ex: "LDU, RF, ULCX",
        "default_trackers" : "LDU",

        "LDU" : {
            "api_key" : "LDU_API_KEY",
            "announce_url" : "https://theldu.net/announce/Custom_Announce_URL",
            "anon" : False,
            "signature" : f"\n[center][b]PLEASE SEED LDU FAMILY[/b][/center]\n[center][size=6][url=https://github.com/z-ink/Upload-Assistant]Upload Assistant(CvT Mod v0.4)[/url][/size][/center]", #Only used if "use_global_sigs" : False,
            "anon_signature" : f"\n[center][size=6]we are anonymous[/size][/center]", #Only used if "use_global_sigs" : False, AND your uploading as "anon" : True, or passing -a at upload
            },   

        "ACM" :{
            "api_key" : "ACM_API_KEY",
            "announce_url" : "https://asiancinema.me/announce/Custom_Announce_URL",
            "anon" : False,
            "signature" : f"\n[center][b]PLEASE SEED ACM FAMILY[/b][/center]\n[center][size=6][url=https://github.com/z-ink/Upload-Assistant]Upload Assistant(CvT Mod v0.4)[/url][/size][/center]",
            "anon_signature" : f"\n[center][size=6]we are anonymous[/size][/center]",          

            # FOR INTERNAL USE ONLY:
            # "internal" : True,
            # "internal_groups" : ["What", "Internal", "Groups", "Are", "You", "In"],
        },

        "AITHER" :{
            "api_key" : "AITHER_API_KEY",
            "announce_url" : "https://aither.cc/announce/Custom_Announce_URL",
            "anon" : False,
            "signature" : f"\n[center][b]PLEASE SEED AITHER FAMILY[/b][/center]\n[center][size=6][url=https://github.com/z-ink/Upload-Assistant]Upload Assistant(CvT Mod v0.4)[/url][/size][/center]",
            "anon_signature" : f"\n[center][size=6]we are anonymous[/size][/center]",                
        },

        "ANT" :{
            "api_key" : "ANT_API_KEY",
            "announce_url" : "https://anthelion.me/announce/Custom_Announce_URL",
            "anon" : False,
            "signature" : f"\n[center][b]PLEASE SEED ANT FAMILY[/b][/center]\n[center][size=6][url=https://github.com/z-ink/Upload-Assistant]Upload Assistant(CvT Mod v0.4)[/url][/size][/center]",
            "anon_signature" : f"\n[center][size=6]we are anonymous[/size][/center]",                
        },

        "BHD" : {
            "api_key" : "BHD_API_KEY",
            "announce_url" : "https://beyond-hd.me/announce/Custom_Announce_URL",
            "draft_default" : "True",
            "anon" : False,
            "signature" : f"\n[center][b]PLEASE SEED BHD FAMILY[/b][/center]\n[center][size=6][url=https://github.com/z-ink/Upload-Assistant]Upload Assistant(CvT Mod v0.4)[/url][/size][/center]",
            "anon_signature" : f"\n[center][size=6]we are anonymous[/size][/center]",               
        },
        "BHDTV": {
            "api_key": "found under https://www.bit-hdtv.com/my.php",
            "announce_url": "https://trackerr.bit-hdtv.com/announce",
            #passkey found under https://www.bit-hdtv.com/my.php
            "my_announce_url": "https://trackerr.bit-hdtv.com/passkey/announce",
            "anon" : "False"
        },   

        "BLU" : {
            "useAPI" : False, # Set to True if using BLU
            "api_key" : "BLU_API_KEY",
            "announce_url" : "https://blutopia.cc/announce/Custom_Announce_URL",
            "anon" : False,
            "signature" : f"\n[center][b]PLEASE SEED BLU FAMILY[/b][/center]\n[center][size=6][url=https://github.com/z-ink/Upload-Assistant]Upload Assistant(CvT Mod v0.4)[/url][/size][/center]",
            "anon_signature" : f"\n[center][size=6]we are anonymous[/size][/center]",             
        },

         "CP2P" : {
            "api_key" : "CP2P_API_KEY",
            "announce_url" : "https://cinemap2p.xyz/announce/Custom_Announce_URL",
            "anon" : False,
            "signature" : f"\n[center][b]PLEASE SEED CP2P FAMILY[/b][/center]\n[center][size=6][url=https://github.com/z-ink/Upload-Assistant]Upload Assistant(CvT Mod v0.4)[/url][/size][/center]",
            "anon_signature" : f"\n[center][size=6]we are anonymous[/size][/center]",             
        },

        "FNP" : {
            "api_key" : "FNP_API_KEY",
            "announce_url" : "https://fearnopeer.com/announce/Custom_Announce_URL",
            "anon" : False,
            "signature" : f"\n[center][b]PLEASE SEED FNP FAMILY[/b][/center]\n[center][size=6][url=https://github.com/z-ink/Upload-Assistant]Upload Assistant(CvT Mod v0.4)[/url][/size][/center]",
            "anon_signature" : f"\n[center][size=6]we are anonymous[/size][/center]",                 
            }, 

        "HDB" : {
            "api_key" : "HDB_API_KEY",
            "announce_url" : "https://https://hdbits.org/announce/Custom_Announce_URL",
            "anon" : False,
            "signature" : f"\n[center][b]PLEASE SEED HDB FAMILY[/b][/center]\n[center][size=6][url=https://github.com/z-ink/Upload-Assistant]Upload Assistant(CvT Mod v0.4)[/url][/size][/center]",
            "anon_signature" : f"\n[center][size=6]we are anonymous[/size][/center]",             
            }, 

        "HDT" : {
            "username" : "username",
            "password" : "password",
            "my_announce_url": "https://hdts-announce.ru/announce.php?pid=<PASS_KEY/PID>",
            "anon" : False,
            "announce_url" : "https://hdts-announce.ru/announce.php", #DO NOT EDIT THIS LINE
        },

        "HP" :{
            "api_key" : "HP_API_KEY",
            "announce_url" : "https://hidden-palace.net/announce/Custom_Announce_URL",
            "anon" : False,
            "signature" : f"\n[center][b]PLEASE SEED HP FAMILY[/b][/center]\n[center][size=6][url=https://github.com/z-ink/Upload-Assistant]Upload Assistant(CvT Mod v0.4)[/url][/size][/center]",
            "anon_signature" : f"\n[center][size=6]we are anonymous[/size][/center]",             
        },

        "HUNO" : {
            "api_key" : "HUNO_API_KEY",
            "announce_url" : "https://hawke.uno/announce/Custom_Announce_URL",
            "anon" : False,
            "signature" : f"\n[center][b]PLEASE SEED HUNO FAMILY[/b][/center]\n[center][size=6][url=https://github.com/z-ink/Upload-Assistant]Upload Assistant(CvT Mod v0.4)[/url][/size][/center]",
            "anon_signature" : f"\n[center][size=6]we are anonymous[/size][/center]",             
        },

        "JPTV" : {
            "api_key" : "JPTV_API_KEY",
            "announce_url" : "https://jptv.club/announce/Custom_Announce_URL",
            "anon" : False,
            "signature" : f"\n[center][b]PLEASE SEED JPTV FAMILY[/b][/center]\n[center][size=6][url=https://github.com/z-ink/Upload-Assistant]Upload Assistant(CvT Mod v0.4)[/url][/size][/center]",
            "anon_signature" : f"\n[center][size=6]we are anonymous[/size][/center]",                 
            }, 

        "LCD" : {
            "api_key" : "LCD_API_KEY",
            "announce_url" : "https://locadora.cc/announce/Custom_Announce_URL",
            "anon" : False,
        },

        "LST" : {
            "api_key" : "LST_API_KEY",
            "announce_url" : "https://lst.gg/announce/Custom_Announce_URL",
            "anon" : False,
            "signature" : f"\n[center][b]PLEASE SEED LST FAMILY[/b][/center]\n[center][size=6][url=https://github.com/z-ink/Upload-Assistant]Upload Assistant(CvT Mod v0.4)[/url][/size][/center]",
            "anon_signature" : f"\n[center][size=6]we are anonymous[/size][/center]",            
        },

        "LT" : {
            "api_key" : "LT_API_KEY",
            "announce_url" : "https://lat-team.com/announce/Custom_Announce_URL",
            "anon" : False,
            "signature" : f"\n[center][b]PLEASE SEED LT FAMILY[/b][/center]\n[center][size=6][url=https://github.com/z-ink/Upload-Assistant]Upload Assistant(CvT Mod v0.4)[/url][/size][/center]",
            "anon_signature" : f"\n[center][size=6]we are anonymous[/size][/center]",             
        },

        "MTV": {
            'api_key' : 'get from security page',
            'username' : '<USERNAME>',
            'password' : '<PASSWORD>',
            'announce_url' : "get from https://www.morethantv.me/upload.php",
            'anon' : False,
            # 'otp_uri' : 'OTP URI, read the following for more information https://github.com/google/google-authenticator/wiki/Key-Uri-Format'
        },

        "NBL" : {
            "api_key" : "NBL_API_KEY",
            "announce_url" : "https://nebulance.io/Custom_Announce_URL",
            "anon" : False,
            "signature" : f"\n[center][b]PLEASE SEED Nebulance FAMILY[/b][/center]\n[center][size=6][url=https://github.com/z-ink/Upload-Assistant]Upload Assistant(CvT Mod v0.4)[/url][/size][/center]",
            "anon_signature" : f"\n[center][size=6]we are anonymous[/size][/center]",             
        },

        "OE" : {
            "api_key" : "OE_API_KEY",
            "announce_url" : "https://onlyencodes.cc/announce/Custom_Announce_URL",
            "anon" : False,
            "signature" : f"\n[center][b]PLEASE SEED OnlyEncodes FAMILY[/b][/center]\n[center][size=6][url=https://github.com/z-ink/Upload-Assistant]Upload Assistant(CvT Mod v0.4)[/url][/size][/center]",
            "anon_signature" : f"\n[center][size=6]we are anonymous[/size][/center]",             
        },

        "PTER" : {
            "passkey":'passkey',
            "img_rehost" : False,
            "username" : "",
            "password" : "",
            "ptgen_api": "",
            "anon": True,
        },

        "PTP" : {
            "useAPI" : False, # Set to True if using PTP
            "add_web_source_to_desc" : True,
            "ApiUser" : "PTP_API_USER",
            "ApiKey" : 'PTP_API_KEY',
            "username" : "",
            "password" : "",
            "announce_url" : ""
        },

        "PTT" :{
            "api_key" : "PTT_API_KEY",
            "announce_url" : "https://polishtorrent.top/announce/Custom_Announce_URL",
            "anon" : False,
            "signature" : f"\n[center][b]PLEASE SEED PolishTorrent FAMILY[/b][/center]\n[center][size=6][url=https://github.com/z-ink/Upload-Assistant]Upload Assistant(CvT Mod v0.4)[/url][/size][/center]",
            "anon_signature" : f"\n[center][size=6]we are anonymous[/size][/center]",             
        },

        "R4E" :{
            "api_key" : "R4E_API_KEY",
            "announce_url" : "https://racing4everyone.eu/announce/Custom_Announce_URL",
            "anon" : False,
            "signature" : f"\n[center][b]PLEASE SEED Racing4Everyone FAMILY[/b][/center]\n[center][size=6][url=https://github.com/z-ink/Upload-Assistant]Upload Assistant(CvT Mod v0.4)[/url][/size][/center]",
            "anon_signature" : f"\n[center][size=6]we are anonymous[/size][/center]",             
        },

        "RF" : {
            "api_key" : "RF_API_KEY",
            "announce_url" : "https://reelflix.xyz/announce/Custom_Announce_URL",
            "anon" : False,
            "signature" : f"\n[center][b]PLEASE SEED ReelFliX FAMILY[/b][/center]\n[center][size=6][url=https://github.com/z-ink/Upload-Assistant]Upload Assistant(CvT Mod v0.4)[/url][/size][/center]",
            "anon_signature" : f"\n[center][size=6]we are anonymous[/size][/center]",             
        },

        "RTF": {
            "api_key": 'get_it_by_running_/api/ login command from https://retroflix.club/api/doc',
            "announce_url": "get from upload page",
            # "tag": "RetroFlix, nd",
            "anon": True,
            "signature" : f"\n[center][b]PLEASE SEED RetroFlix FAMILY[/b][/center]\n[center][size=6][url=https://github.com/z-ink/Upload-Assistant]Upload Assistant(CvT Mod v0.4)[/url][/size][/center]",
            "anon_signature" : f"\n[center][size=6]we are anonymous[/size][/center]",             
        },

        "SN": {
            "api_key": "SN_API_KEY",
            "announce_url": "https://tracker.swarmazon.club:8443/<YOUR_PASSKEY>/announce",
            "anon" : False,
            "signature" : f"\n[center][b]PLEASE SEED Swamazon FAMILY[/b][/center]\n[center][size=6][url=https://github.com/z-ink/Upload-Assistant]Upload Assistant(CvT Mod v0.4)[/url][/size][/center]",
            "anon_signature" : f"\n[center][size=6]we are anonymous[/size][/center]", 
        },
        "STC" :{
            "api_key" : "STC_API_KEY",
            "announce_url" : "https://skipthecommericals.xyz/announce/Custom_Announce_URL",
            "anon" : False,
            "signature" : f"\n[center][b]PLEASE SEED SkipTheCommercials FAMILY[/b][/center]\n[center][size=6][url=https://github.com/z-ink/Upload-Assistant]Upload Assistant(CvT Mod v0.4)[/url][/size][/center]",
            "anon_signature" : f"\n[center][size=6]we are anonymous[/size][/center]",             
        },
        "STT" :{
            "api_key" : "STT_API_KEY",
            "announce_url" : "https://skipthetrailers.xyz/announce/Custom_Announce_URL",
            "anon" : False,
            "signature" : f"\n[center][b]PLEASE SEED SkipTheTrailers FAMILY[/b][/center]\n[center][size=6][url=https://github.com/z-ink/Upload-Assistant]Upload Assistant(CvT Mod v0.4)[/url][/size][/center]",
            "anon_signature" : f"\n[center][size=6]we are anonymous[/size][/center]",             
        },

        "TDC" :{
            "api_key" : "TDC_API_KEY",
            "announce_url" : "https://thedarkcommunity.cc/announce/Custom_Announce_URL",
            "anon" : False,
            "signature" : f"\n[center][b]PLEASE SEED DarkCommunity[/b][/center]\n[center][size=6][url=https://github.com/z-ink/Upload-Assistant]Upload Assistant(CvT Mod v0.4)[/url][/size][/center]",
            "anon_signature" : f"\n[center][size=6]we are anonymous[/size][/center]",             
        },

        "THR" : {
            "username" : "username",
            "password" : "password",
            "img_api" : "get_this_from_the_forum_post",
            "announce_url" : "http://www.torrenthr.org/announce.php?passkey=yourpasskeyhere",
            "pronfo_api_key" : "pronfo_API_KEY",
            "pronfo_theme" : "pronfo theme code",
            "pronfo_rapi_id" : "pronfo remote api id",
            "anon" : False,
        },

        "TL": {
            "announce_key": "TL_announce_key",
        },

    	'TTR' : {
	    'api_key' : 'TTR_API_KEY',
	    'announce_url' : 'https://torrenteros.org/announce/Custom_Announce_URL',
	    'anon' : 'False',
	    'signature' : '\n[center][b]PLEASE SEED TorrentEros FAMILY[/b][/center]\n[center][size=6][url=https://github.com/z-ink/Upload-Assistant]Upload Assistant(CvT Mod v0.4)[/url][/size][/center]',
	    'anon_signature' : '\n[center][size=6]we are anonymous[/size][/center]'
	},
	    
        "ULCX" : {
            "api_key" : "ULCX_API_KEY",
            "announce_url" : "https://upload.cx/announce/Custom_Announce_URL",
            "anon" : False,
            "signature" : f"\n[center][b]PLEASE SEED ULCX FAMILY[/b][/center]\n[center][size=6][url=https://github.com/z-ink/Upload-Assistant]Upload Assistant(CvT Mod v0.4)[/url][/size][/center]",
            "anon_signature" : f"\n[center][size=6]we are anonymous[/size][/center]",            
        },
	    
        "MANUAL" : {
            # Uncomment and replace link with filebrowser (https://github.com/filebrowser/filebrowser) link to the Upload-Assistant directory, this will link to your filebrowser instead of uploading to uguu.se
            # "filebrowser" : "https://domain.tld/filebrowser/files/Upload-Assistant/"
        },
    },


    "TORRENT_CLIENTS" : {
        # Name your torrent clients here, for example, this example is named "Client1"
        "Client1" : {
            "torrent_client" : "qbit",
            "qbit_url" : "http://127.0.0.1",
            "qbit_port" : "8080",
            "qbit_user" : "username",
            "qbit_pass" : "password",

            # Remote path mapping (docker/etc.) CASE SENSITIVE
            # "local_path" : "/LocalPath",
            # "remote_path" : "/RemotePath"
        },
        "qbit" : { #SAMPLE
            "torrent_client" : "qbit",
            "enable_search" : True,
            "qbit_url" : "http://127.0.0.1",
            "qbit_port" : "8080",
            "qbit_user" : "username",
            "qbit_pass" : "password",
            # "torrent_storage_dir" : "path/to/BT_backup folder",
            # "qbit_tag" : "tag",
            # "qbit_cat" : "category",
            
            # Content Layout for adding .torrents: "Original"(recommended)/"Subfolder"/"NoSubfolder"
            "content_layout" : "Original",
            
            # Enable automatic torrent management if listed path(s) are present in the path
                # If using remote path mapping, use remote path
                # For using multiple paths, use a list ["path1", "path2"] 
            # "automatic_management_paths" : "",



            # Remote path mapping (docker/etc.) CASE SENSITIVE
            # "local_path" : "E:\\downloads\\tv",
            # "remote_path" : "/remote/downloads/tv",

            # Set to True to verify certificate for HTTPS connections; for instance, if the connection is using a self-signed certificate.
            "VERIFY_WEBUI_CERTIFICATE" : False,
        },

        "rtorrent" : { #SAMPLE
            "torrent_client" : "rtorrent",
            "rtorrent_url" : "https://user:password@server.host.tld:443/username/rutorrent/plugins/httprpc/action.php",
            # "torrent_storage_dir" : "path/to/session folder",
            # "rtorrent_label" : "Add this label to all uploads",

            # Remote path mapping (docker/etc.) CASE SENSITIVE
            # "local_path" : "/LocalPath",
            # "remote_path" : "/RemotePath",

        },
        "deluge" : { #SAMPLE
            "torrent_client" : "deluge",
            "deluge_url" : "localhost",
            "deluge_port" : "8080",
            "deluge_user" : "username",
            "deluge_pass" : "password",
            # "torrent_storage_dir" : "path/to/session folder",
            
            # Remote path mapping (docker/etc.) CASE SENSITIVE
            # "local_path" : "/LocalPath",
            # "remote_path" : "/RemotePath"
        },
        "watch" : { #SAMPLE
            "torrent_client" : "watch",
            "watch_folder" : "/Path/To/Watch/Folder",
        },

    },


    "DISCORD" :{
        "discord_bot_token" : "discord bot token",
        "discord_bot_description" : "Upload Assistant",
        "command_prefix" : "!",
        "discord_channel_id" : "discord channel id for use",
        "admin_id" : "your discord user id",

        "search_dir" : "Path/to/downloads/folder/   this is used for search",
        # Alternatively, search multiple folders:
        # "search_dir" : [
        #   "/downloads/dir1",
        #   "/data/dir2",
        # ]
        "discord_emojis" : {
                "BLU": "💙",
                "BHD": "🎉",
                "AITHER": "🛫",
                "STC": "📺",
                "ACM": "🍙",
                "MANUAL" : "📩",
                "UPLOAD" : "✅",
                "CANCEL" : "🚫"
        }
    }
}


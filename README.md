# ![Uploadrr by CvT](https://i.ibb.co/2NVWb0c/uploadrr.webp)

# Uploadrr

Welcome to a tool which aims to make your life easier just to give you a headache when it all breaks down. Yay code!
Help is always apreciated, yes it should be rebuilt from the ground up. No, nobody has time for that. We stand on the shoulder of giants.. or are lazy. 
Coffee timeeee.

> [!NOTE]
> This project is a fork of an existing repository, which I have customized for me n friends. While it retains core functionality from the original project, there may be slight variations to better suit my needs. You are welcome to use this fork as you see fit.

## Features
  - **Media Information:** Generates and parses MediaInfo/BDInfo.
  - **Screenshots:** Generates and uploads screenshots.
  - **Filename Correction:** Uses srrdb to fix scene filenames.
  - **Descriptions:** Retrieves descriptions from PTP (automatically on filename match or via argument) / BLU (via argument).
  - **Identifiers:** Obtains TMDb/IMDb/MAL identifiers.
  - **Anime Season/Episode Numbering:** Converts absolute to season and episode numbering for anime.
  - **Custom Torrents:** Generates custom .torrents without unnecessary top-level folders or .nfo files.
  - **Reuse Torrents:** Reuses existing torrents instead of creating new ones.
  - **Naming:** Generates appropriate names for your uploads using MediaInfo/BDInfo and TMDb/IMDb, conforming to site rules.
  - **Duplicate Check:** Checks for existing releases on the site.
  - **Queuing:** Supports manual or automated queuing.
  - **Client Integration:** Adds to your client with fast resume, seeding instantly (compatible with rtorrent/qbittorrent/deluge/watch folder).
  - **Minimal Input Required:** Operates with minimal user input.
  - **File Formats:** Currently supports .mkv, .mp4, Blu-ray, DVD, HD-DVDs (or any format with --full-directory applied).

## Supported Sites

<div align="center">

<details>
<summary>Click Here For Sites List</summary>

| ABV  | Sitename | Notes |
|------|----------|-------|
| ACM  |     AsianCinema     |       |
| AITHER|      Aither    |       |
| ANT  |      Anthelion    |       |
| AR   |      Alpha Ratio    |    Movies/TV Only   |
| BHD|     Beyond HD    |       |
| BHDTV|     Beyond HD TV     |       |
| BLU  |     Blutopia     |       |
| CBR  |     Capybara BR     |       |
| FL   |      File List    |       |
| FNP  |    Fear No Peer      |       |
| HDB  |      HD Bits    |       |
| HDT  |     HD Torrents     |       |
| HHD  |      Homie Help Desk    |       |
| HUNO |      Hawke uno    |       |
| ITA  |     ItaTorrents     |  Requires Upload Privs  |
| JPTV |       JPTV Club   |       |
| LCD  |     Locadora    |       |
| LDU  |    The Last Digital Underground      |      |
| LST  |     LST     |       |
| LT   |       Lat-Team   |       |
| MB   |     MalayaBits     |       |
| MTV  |      More than TV    |       |
| NBL  |     Nebulance     |       |
| OE   |     OnlyEncodes     |       |
| OINK |     YOiNKED     |       |
| OTW  |     Old Toons World     |       |
| PSS  |     Private Silver Screen     |       |
| PTER |     PTER     |       |
| PTT  |     Polish Torrent     |       |
| R4E  |     Racing4Everyone     |    Limited   |
| RF   |    ReelFLiX      |       |
| RHD  |    RocketHD      |       |
| RTF  |      RetroFlix    |       |
| SHRI |     Share Island     |       |
| SN   |    Swarmazon      |       |
| TTG  |     TorrentHR     |       |
| TL   |     TorrentLeech     |   Requires Upload Privs    |
| TTG  |     To The Glory     |       |
| TTR  |      Torrent Eros    |       |
| ULCX |      Upload    |       |
| UTP  |     Utopia     |       |
| YU  |     YU-Scene     |       |

</details>

</div>

> [!TIP]
> To ensure proper functionality with Uploadrr, please use the exact ABV name as listed in list. 

## Upcoming Features
  - Enhanced support for FANRES & Adult Content.
  - Improved support for Music & Ebooks.

## Setup
1) **Prerequisites:**
   - Python 3.7 or higher, with pip3.
     - For Python 3.7, install qbittorrent-api==2023.9.53 or a compatible version.
   - [Mono](https://www.mono-project.com/) is required on Linux systems for BDInfo.
   - MediaInfo and ffmpeg must be installed.
2) **Installation:**
   - **Windows:** Add ffmpeg to PATH. Use [Scoop](https://scoop.sh/) for easy installation or follow this [manual guide](https://windowsloop.com/install-ffmpeg-windows-10/).
   - **Linux:** Install ffmpeg via your package manager.
   - **MacOS:** Install ffmpeg using Homebrew or place static builds in `/usr/bin` or `$HOME/.local/bin`. Update PATH in `$HOME/.zshrc` with `export PATH="$PATH:$HOME/.local/bin"`.
3) **Clone the Repository:**
     ```
     git clone https://codeberg.org/CvT/Uploadrr.git
     ```
4) **Configure:**
   - Copy and rename `data/backup/example-config.py` to `data/config.py`.
   - Edit `config.py` with your information. Detailed instructions are available in the [wiki](https://github.com/L4GSP1KE/Upload-Assistant/wiki).
     - Obtain a TMDb API (v3) key from [TMDb](https://developer.themoviedb.org/docs/getting-started).
     - Acquire image host API keys from their respective sites.
   - Install necessary Python modules:
     ```
     pip3 install --user -U -r requirements.txt
     ```    
   
## Updating
To update your installation:
1) Navigate to the Uploadrr directory:
   ```
   cd Uploadrr
   ```
2) Pull the latest changes:
   ```
   git pull
   ```
3) Update Python dependencies:
   ```
   python3 -m pip install --user -U -r requirements.txt
   ```

## CLI Usage

Run the tool using:
```
python3 upload.py "/path/to/media" --args
```
Example: 
```
python3 upload.py "/home/regedits/torrents/qbittorrent/uploads/Avengers.Age.of.Ultron.2015.2160p.DSNP.WEB-DL.DDP5.1.Atmos.DV.HDR.H.265-RegEdits.mkv" --args -tk LDU -ns -pr -d [code]This release is sourced from DisneyPlus[/code]
```

Arguments are optional. For a list of acceptable arguments, use `--help`. For an overview of arguments with descriptions, navigate to the [Uploadrr Arguments List](https://theldu.org/index.php/Uploadrr).

## Docker Usage
Special thanks to __l1mo__ for the Dockerfile setup and __dare__ for the command. Run the tool using Docker with one of the following commands:
```
docker run --rm -it --network=host \
-v /path/to/config.py:/Uploadrr/data/config.py \
-v /path/to/media:/media \
-v /path/to/BT_backup:/BT_backup \
codeberg.org/CvT/Uploadrr:master "/path/to/media" --args
```
__OR__
```
docker run --rm -it --network=host -v /path/to/config.py:/Uploadrr/data/config.py -v /path/to/media:/media -v /path/to/BT_backup:/BT_backup codeberg.org/CvT/Uploadrr:master "/path/to/media" --args
```


## Aknowledgements
All credit for the building blocks of the project goes to __L4G__ (and collaborators): [Original Repo Here](https://github.com/L4GSP1KE/Upload-Assistant) 

The reson for a rename isn't to discredit or steal it rather to create a distinction that the project isnt compatible. I've gone and coded in a reconfiguration script to make old configs compatible but as time goes on the code will start stray further and further away as code is restructured dependancies dropped and added as needed. I thank everyone for their time and energy in going to improving the old script and this one here. Many hands make light work. :)
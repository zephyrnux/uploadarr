import os
import re
import copy
import operator
import pprint
import argparse
from rich import print as Print
from rich.console import Console
from rich.prompt import Prompt
from packaging import version

console = Console()

class DoubleQuoteDict(dict):
    def __str__(self):
        return "{" + ", ".join(f"\"{k}\": {v if not isinstance(v, str) else '\"' + v.replace('\n', '\\n') + '\"'}" for k, v in self.items()) + "}"

class CustomPrettyPrinter(pprint.PrettyPrinter):
    def _format(self, object, stream, indent, allowance, context, level):
        if isinstance(object, dict):
            stream.write("{\n")
            self._indent_per_level += 1
            for i, (key, value) in enumerate(object.items()):
                if level == 1:
                    stream.write("    ")
                if level == 2:
                    stream.write("            ")        
                if isinstance(value, dict):
                    stream.write(f"\"{key}\": ")
                    self._format(value, stream, indent, allowance + 1, context, level + 1)
                else:
                    stream.write(f"\"{key}\": {value if not isinstance(value, str) else '\"' + value.replace('\n', '\\n') + '\"'}")
                if i < len(object) - 1: 
                    stream.write(",")
                    if level == 0 or 1 and isinstance(value, dict):
                        stream.write("\n\n")
                    else:
                        stream.write("\n")                     
            self._indent_per_level -= 1
            stream.write("\n}")
        else:
            super()._format(object, stream, indent, allowance, context, level)

def read_config(file_path):
    with open(file_path, 'r') as file:
        exec(file.read())
    return locals()['config']

def write_config(file_path, config_dict):
    with open(file_path, 'w') as file:
        file.write(f"\n        ##---------THE LAST DIGITAL UNDERFROUND PRESENTS-------##\n        ##                                                     ##\n        ##                 Special Recruitment :)              ##\n        ##          @ https://TheLDU.to/application            ##\n        ##                                                     ##\n        ##                              Ref: Uploadrr by CvT   ##\n        ##-._.-._.-._.-._.-._.-._.-._.-._.-._.-._.-._.-._.-._.-##\n\n  #Refer to `/backup/example-config.py` for additional options + comments\n\n")
        file.write('config = ')
        printer = CustomPrettyPrinter(stream=file)
        printer.pprint(config_dict)


def replace_values(base_dict, old_dict):
    special_cases = {
        'global_sig': '\n[center][size=6][url=https://github.com/z-ink/Upload-Assistant]Upload Assistant(CvT Mod v0.4)[/url][/size][/center]',
        'global_anon_sig': '\n[center][size=6]we are anonymous[/size][/center]',
        'anon_signature': '\n[center][size=6]we are anonymous[/size][/center]'
    }

    for key, old_value in old_dict.items():
        if key in base_dict:
            if key == 'version':
                continue
            if isinstance(old_value, dict):
                replace_values(base_dict[key], old_value)
                continue

            else:
                if key in special_cases and old_value == special_cases[key]:
                    continue
                elif key == 'signature':
                    if key in special_cases:
                        base_dict[key] = special_cases[key]
                    else:
                        match = re.search(r'PLEASE SEED (.*) FAMILY', old_value)
                        if match:
                            continue
                        elif "[size=6][url=https://github.com/z-ink/Upload-Assistant]Upload Assistant(CvT Mod v0.4)[/url][/size]" in old_value:
                            base_dict[key] = old_value.replace("[size=6][url=https://github.com/z-ink/Upload-Assistant]Upload Assistant(CvT Mod v0.4)[/url][/size]", "[url=https://github.com/z-ink/Uploadrr][img=400]https://i.ibb.co/2NVWb0c/uploadrr.webp[/img][/url]")
                        elif "[size=6][url=https://github.com/z-ink/Upload-Assistant]Upload Assistant(CvT Mod v0.3)[/url][/size]" in old_value:
                            base_dict[key] = old_value.replace("[size=6][url=https://github.com/z-ink/Upload-Assistant]Upload Assistant(CvT Mod v0.3)[/url][/size]", "[url=https://github.com/z-ink/Uploadrr][img=400]https://i.ibb.co/2NVWb0c/uploadrr.webp[/img][/url]")
                        elif "[url=https://github.com/z-ink/Upload-Assistant]" in old_value:
                            base_dict[key] = old_value.replace("https://github.com/z-ink/Upload-Assistant", "https://github.com/z-ink/Uploadrr")
                        else:
                            base_dict[key] = old_value
                else:
                    base_dict[key] = old_value                            
        else:
            base_dict[key] = old_value



parser = argparse.ArgumentParser(description='Reconfigure the config file.')
parser.add_argument('--output-dir', type=str, required=True, help='The directory where the new config.py should be written.')
args = parser.parse_args()
output_dir = args.output_dir

data_dir = os.path.dirname(os.path.realpath(__file__))
backup_dir = os.path.join(data_dir, 'backup')

def reconfigure():
    base_config = read_config(os.path.join(backup_dir, 'example_config.py'))
    old_config = read_config(os.path.join(backup_dir, 'old_config.py'))
    new_config = copy.deepcopy(base_config)
    replace_values(new_config, old_config)

    if os.path.exists(os.path.join(backup_dir, 'config.py')):
        current_config = read_config(os.path.join(backup_dir, 'config.py'))
    else:
        current_config = {'version': '0'}

    if not os.path.exists(os.path.join(backup_dir, 'old_config.py')):
        console.print("[bold red]WARN[/bold red]: [bold]old_config.py[/bold] not found, please rename your old `config.py` to `old_config.py` and try again")
        return

    if os.path.exists(os.path.join(backup_dir, 'config.py')):
        if version.parse(current_config.get('version', '0')) > version.parse(base_config.get('version', '0')):
            console.print("[bold red]WARN[/bold red]: The current config file has a higher version number than the example config file.")
            console.print("[bold red]WARN[/bold red]: Continuing will [bold]downgrade[/bold] the configuration file and may cause [bold]incompatibility issues[/bold].")
            overwrite = Prompt.ask("Do you wish to continue?", choices=["y", "N"], default="N")
            if overwrite.lower() != 'y':
                return
        else:
            overwrite = Prompt.ask("[bold red]WARN[/bold red]: [bold]config.py[/bold] exists, if you continue you will [bold]OVERWRITE[/bold] your current config, do you wish to continue?", choices=["y", "N"], default="N")
            if overwrite.lower() != 'y':
                return

    # Add additional TRACKERS
    added_blocks = []
    for key in old_config['TRACKERS']:
        if key not in new_config['TRACKERS']:
            new_config['TRACKERS'][key] = old_config['TRACKERS'][key]
            added_blocks.append(key)
    
    default_value = new_config['TRACKERS'].pop('default_trackers', None)
    
    # Sort TRACKERS alphabetically
    new_config['TRACKERS'] = dict(sorted(new_config['TRACKERS'].items(), key=operator.itemgetter(0)))
    
    if default_value is not None:
        new_config['TRACKERS'] = {'default_trackers': default_value, **new_config['TRACKERS']}

    write_config(os.path.join(output_dir, 'config.py'), new_config)

    Print('[bold green]Congratulations! config.py was successfully updated.[/bold green]')
    Print('[bold yellow]WARN[/bold yellow]: It is recommended you double check your client settings.')
    if added_blocks:
        Print('[bold yellow]WARN[/bold yellow]: The following [i]not built-in[/i] TRACKERS: [bold]' + '[/bold], [bold]'.join(added_blocks) + '[/bold] were added.') 
        Print('[bold yellow]WARN[/bold yellow]: Please be sure to add them in `upload.py` and add the .py files into `/src/trackers`')

reconfigure()

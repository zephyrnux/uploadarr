import os
import copy
import operator
import pprint
from rich import print as Print
from rich.prompt import Prompt
from rich.console import Console
from packaging import version

class CustomPrettyPrinter(pprint.PrettyPrinter):
    def _format(self, object, stream, indent, allowance, context, level):
        if isinstance(object, dict):
            stream.write('{\n')
            self._indent_per_level += 1
            for i, (key, value) in enumerate(object.items()):
                if level == 1:
                    stream.write('    ')
                if level == 2:
                    stream.write('            ')        
                self._format(key, stream, indent, allowance + 1, context, level + 1)
                stream.write(' : ')
                if isinstance(value, dict):
                    self._format(value, stream, indent, allowance + 1, context, level + 1)
                else:
                    stream.write(repr(value))
                if i < len(object) - 1: 
                    stream.write(',')
                    if level == 0 or 1 and isinstance(value, dict):
                        stream.write('\n\n')
                    else:
                        stream.write('\n')
            self._indent_per_level -= 1
            stream.write('\n}')
        else:
            super()._format(object, stream, indent, allowance, context, level)

def read_config(file_path):
    with open(file_path, 'r') as file:
        exec(file.read())
    return locals()['config']

def write_config(file_path, config_dict):
    with open(file_path, 'w') as file:
        file.write('config = ')
        printer = CustomPrettyPrinter(stream=file)
        printer.pprint(config_dict)

def replace_values(base_dict, old_dict):
    for key in old_dict:
        if key in base_dict:
            if key == 'version': 
                continue
            if isinstance(old_dict[key], dict):
                replace_values(base_dict[key], old_dict[key])
            else:
                base_dict[key] = old_dict[key]

console = Console()
script_dir = os.path.dirname(os.path.realpath(__file__))
data_dir = os.path.join(script_dir, 'data')

def reconfigure():
    base_config = read_config(os.path.join(data_dir, 'example_config.py'))
    old_config = read_config(os.path.join(data_dir,'old_config.py'))
    new_config = copy.deepcopy(base_config)
    replace_values(new_config, old_config)

    if os.path.exists(os.path.join(data_dir,'config.py')):
        current_config = read_config(os.path.join(data_dir,'config.py'))
    else:
        current_config = {'version': '0'} 

    if not os.path.exists(os.path.join(data_dir, 'old_config.py')):
        console.print("[bold red]WARN[/bold red]: [bold]old_config.py[/bold] not found, please rename your old `config.py` to `old_config.py` and try again")
        return


    if os.path.exists(os.path.join(data_dir,'config.py')):
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

    write_config(os.path.join(data_dir,'config.py'), new_config)

    Print('[bold green]Congratulations![/bold green] config.py was successfully updated.')
    Print('[bold yellow]WARN[/bold yellow]: It is recommended you double check your client settings.')
    if added_blocks:
        Print('[bold yellow]WARN[/bold yellow]: The following [i]non-included[/i] TRACKERS: [bold]' + '[/bold], [bold]'.join(added_blocks)+'[/bold] were added.') 
        Print('[bold yellow]WARN[/bold yellow]: Please be sure to add them in upload.py and add the .py files into /src/trackers')
        

reconfigure()

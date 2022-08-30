import json, argparse, re
import IPython, sys

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--commands", default=None, help="Commands txt file")
    parser.add_argument("--commands-tables", default=None, help="Commands with tables txt file")
    parser.add_argument("--output", default="dom5map-snippets.json", help="Output json file for snippets")
    args = parser.parse_args()
    # first get snippet spec from txt file
    snippet_spec = {}
    current_command_type = None
    if args.commands is not None:
        print(f"reading file {args.commands}")
        with open(args.commands, "r", encoding="utf8") as f:
            commands = f.readlines()
        # parse file
        for commandline in commands:
            if len(commandline.strip()) <= 0:
                continue
            line_splt = commandline.split("::") # this should split into two
            assert len(line_splt) == 2, "Line has multiple instances of :: in it"
            if not line_splt[0].strip().startswith("#"):
                # this is a command type
                current_command_type = line_splt[0].strip()
                snippet_spec[current_command_type] = {"_desc": line_splt[1]}
            if current_command_type is not None and line_splt[0].strip().startswith("#"):
                # this is a command
                current_command_spec = line_splt[0].strip()
                # this is the current command spec e.g. #commandname <arg1> <arg2> ...
                cc_splt = current_command_spec.split()
                current_command = cc_splt[0]
                snippet_spec[current_command_type][current_command_spec] = line_splt[1]
    
    # next step is to generate table snippets
    command_table_spec = {}
    if args.commands_tables is not None:
        print(f"reading file {args.commands}")
        with open(args.commands_tables, "r", encoding="utf8") as f:
            commands_tables = f.readlines()
        # parse file
        table_name = None
        for line in commands_tables:
            line = line.strip()
            if line == "---":
                # we are done with table
                table_name = None
                continue
            line_splt = line.split(":")
            if len(line_splt) == 2:
                # this is a table description
                table_name = line_splt[0]
                table_desc = line_splt[1]
                command_table_spec[table_name] = {}
                command_table_spec[table_name]["_desc"] = table_desc
                continue
            else:
                try:
                    val = int(line_splt[0])
                    # this is a table value
                    snip_txt = line_splt[1]
                    snip_desc = line_splt[2]
                    command_table_spec[table_name][snip_txt] = {}
                    command_table_spec[table_name][snip_txt]["value"] = val
                    command_table_spec[table_name][snip_txt]["_desc"] = snip_desc
                    continue
                except ValueError as e:
                    print(e)
                    IPython.embed()
                    raise e

    # build up snippet dictionary
    snippets = {}

    for command_type in snippet_spec:
        # these are types of commands
        for command_spec in snippet_spec[command_type]:
            if command_spec.startswith("_"):
                continue
            # this is the spec and description
            # break the spec down
            m1 = re.match(r'^(#\w+)\s*(.*)', command_spec)
            command_name = m1.group(1)
            args_match = m1.group(2)
            if len(args_match) > 0:
                # we have arguments
                arg_list = []
                # if "province" in args:
                #     IPython.embed();sys.exit()
                m3 = re.findall(r'(“[\.A-Za-z0-9 <>-]+”)+', args_match)
                for match_str in m3:
                    args_match = args_match.replace(match_str,"")
                m2 = re.findall(r'(<[\.A-Za-z0-9 ^“^”-]+>)+', args_match)
                if m2 is not None:
                    arg_list += m2
                if m3 is not None:
                    arg_list += m3

            snippet_name = f"{command_type}:{command_name}"
            snippets[snippet_name] = {}
            snippets[snippet_name]["description"] = snippet_spec[command_type][command_spec][1:]
            snippets[snippet_name]["prefix"] = command_name
            snippets[snippet_name]["body"] = []
            body_str = command_name
            for iarg, arg in enumerate(arg_list):
                body_str += " ${" 
                body_str += f"{iarg}:{arg}"
                body_str += "}"
            
            snippets[snippet_name]["body"].append(body_str)

    #        "Commander:#mag_nature": {
    #     "description": "Gives active commander Nature magic.\n",
    #     "prefix": "#mag_nature",
    #     "body": [
    #         "#mag_nature ${0:<level>}"
    #     ]
    # }, 
    # now add table snippets
    for table_name in command_table_spec:
        table = command_table_spec[table_name]
        for snip in table:
            if snip.startswith("_"):
                continue
            # snip is the "prefix" and the value is the body
            snippet_name = f"{table_name}-{snip}"
            snippets[snippet_name] = {}
            snippets[snippet_name]["description"] = f'{table["_desc"]}:{table[snip]["_desc"]}'
            snippets[snippet_name]["prefix"] = snip
            snippets[snippet_name]["body"] = [str(table[snip]["value"])]

    # dump json
    with open(args.output, "w+", encoding="utf8") as f:
        print(f"writing file {args.output}")
        json.dump(snippets, f, ensure_ascii=False, indent=4)
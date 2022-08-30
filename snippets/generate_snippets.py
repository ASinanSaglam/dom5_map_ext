import json, argparse, re
import IPython, sys

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--commands", default=None, help="Commands txt file")
    parser.add_argument("--commands-tables", default=None, help="Commands with tables txt file")
    parser.add_argument("--output", default="dom5map-snippets.json", help="Output json file for snippets")
    args = parser.parse_args()

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
    # IPython.embed();sys.exit()
    if args.commands_tables is not None:
        with open(args.commands_tables, "r", encoding="utf8") as f:
            commands_tables = f.readlines()
        # parse file

    # "CompartmentLine": {
    #     "scope": "bngl",
    #     "prefix": "CompartmentLine",
    #     "body": [
    #         "${1:CompartmentName} ${2|2,3|} ${3:volume} ${4:ParentCompartment}$0"
    #     ]
    # },

    snippets = {}

    for command_type in snippet_spec:
        # these are types of commands
        for command_spec in snippet_spec[command_type]:
            if command_spec.startswith("_"):
                continue
            # this is the spec and description
            # break the spec down
            m1 = re.match(r'^(#\w+)\s*(.*)', command_spec)
            command_name = m1.group(0)
            args = m1.group(1)
            if len(args) > 0:
                # we have arguments
                m2 = re.match(r'(<\w+>)', args)
                IPython.embed();sys.exit()
            # spec_splt = command_spec.split("<")
            # if len(spec_splt) > 1 and "“" in command_spec:
            #     splt_arg_list = spec_splt[1:]
            #     spec_splt = [spec_splt[0]]
            #     spec_splt += functools.reduce(lambda x,y: x+y, [i.split("“") for i in splt_arg_list])
            # command_name = ""
            # arg_list = []
            # for sp in spec_splt:
            #     sp = sp.strip()
            #     if sp.endswith(">"):
            #         # this is an argument
            #         arg_list.append("<"+sp)
            #     elif sp.endswith('”'):
            #         # this is an argument
            #         arg_list.append("“"+sp)
            #     else:
            #         command_name += sp
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
    
    # dump json
    with open(args.output, "w+", encoding="utf8") as f:
        print(f"writing file {args.output}")
        json.dump(snippets, f, ensure_ascii=False, indent=4)
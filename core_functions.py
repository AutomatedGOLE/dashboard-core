# Configuration file parser
def parse_config(log_file):
    options = {}
    f = open(log_file)
    for line in f:
        # First, remove comments:
        if '#' in line:
            # split on comment char, keep only the part before
            line, comment = line.split('#', 1)
        # Second, find lines with an option=value:
        if '=' in line:
            # split on option char:
            option, value = line.split('=', 1)
            # strip spaces:
            option = option.strip()
            value = value.strip()
            # store in dictionary:
            options[option] = value
    f.close()
    return options

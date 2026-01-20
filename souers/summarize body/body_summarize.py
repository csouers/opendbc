import re

# Read the DBC file
with open('HONDA_BODY_MASTER.dbc', 'r') as file:
    dbc_content = file.read()

# Extract all messages and group by module
module_messages = {}
for line in dbc_content.split('\n'):
    if line.startswith('BO_'):
        # Extract the decimal ID and message name from the line
        match = re.search(r'BO_ (\d+) ([^:]+):', line)
        if match:
            decimal_id = int(match.group(1))
            message_name = match.group(2)
            # Convert to hex and format properly
            hex_id = hex(decimal_id)[2:].upper()  # Convert to hex and remove '0x'
            # Remove the trailing byte (last 2 characters)
            if len(hex_id) > 2:
                formatted_id = hex_id[:-2]  # Remove last 2 characters (trailing byte)
            else:
                formatted_id = hex_id  # Keep as is if too short
            # Extract the module name (last part of the line)
            module_name = line.split()[-1]
            # Add message to module's list
            if module_name not in module_messages:
                module_messages[module_name] = []
            module_messages[module_name].append((formatted_id, message_name))

# Print all messages grouped by module in markdown format
print("# DBC File Message Summary\n")
for module in sorted(module_messages.keys()):
    print(f"## {module}\n")
    for msg_id, msg_name in sorted(module_messages[module]):
        print(f"- `{msg_id}` - {msg_name}")
    print()  # Empty line between modules

# urh-ETH_Comfort_decode_plugin
Universal Radio Hacker (urh) external decoding plugin to decode eQ-3/Technoline ETH Comfort messages, which
use Manchester code and bit stuffing

simply set the permissions to 755 to make the script executable:
chmod 755 urh-ETH_Comfort_decode_plugin.py

start the plugin in urh as external program with:
urh-ETH_Comfort_decode_plugin.py

Each telegram consists of multiple repetitions, each one starts with 0x7E.

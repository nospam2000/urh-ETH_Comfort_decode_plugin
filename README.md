# urh-ETH_Comfort_decode_plugin.py
Universal Radio Hacker (urh) plugin to decode eQ-3/Technoline ETH Comfort messages, which
use Manchester code and bit stuffing

external decoding plugin for eQ-3/Technoline ETH Comfort Manchester code in urh.

simply set the permissions to 755 to make the script executable:
chmod 755 urh-ETH_Comfort_decode_plugin.py

start the plugin in urh as external program with:
urh-ETH_Comfort_decode_plugin.py

The telegram consists of multiple repetitions, each one starts with 0x7E.

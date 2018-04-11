# urh-ETH_Comfort_decode_plugin
Universal Radio Hacker (urh) external decoding plugin to decode eQ-3/ELV/Technoline ETH comfort messages, which
use Manchester code and bit stuffing.

Actually the plugin implements SDLC/HDLC decoding and encoding so it might also work with other protocols:
 * sync word = 0110101010101001 (decoded this will show up as 0x7E)
 * LSB (least significant bit) is sent first
 * use Manchester code (01 => 0, 10 => 1)
 * stuff one zero-bit (01) after 5 one-bits (10), except in the sync word

To use the plugin you need to have python installed. Under Linux/Mac OSX set the permissions to 755 to make the script executable:
chmod 755 urh-ETH_Comfort_decode_plugin.py

start the plugin in urh as external **decoding** program with:
urh-ETH_Comfort_decode_plugin.py **d**


to use it as external **encoding** program, use the following parameter:
urh-ETH_Comfort_decode_plugin.py **e**


Refer to https://github.com/jopohl/urh/wiki/Decodings#work-with-decodings for more information on how to use external decoding.

Each telegram consists of multiple repetitions, each one starts with 0x7E.

#!/usr/bin/env python
# Purpose:
#   Decode the eQ-3/Technoline ETH Comfort 200/300 lowlevel bitstream which is used by
#   radio controlled heating valve (Heizkoerperthermostat), remote control (Fernbedienungen),
#   room thermostate (Raumthermostate), temperature sensors (Temperatursensoren).
#   This Script is made to be used by URH (Universal Radio Hacker) as 'External Program' decoding
#   Because the builtin Manchester 2 decoding doesn't do the stream synchronization and the bit de-stuffing.

#   More information can be found
#     in the discussion thread https://www.mikrocontroller.net/topic/172034
#     in the discussing thread https://jeelabs.net/boards/7/topics/2626

# Copyright (c) 2018 by Michael Dreher <michael(a)5dot1.de>
# Multi-License: you can either use the GNU General Public License v3.0 or the MIT license

import sys

def printByte(byte) :
	sys.stdout.write("{:08b}".format(byte)) # output format for URH
	#sys.stdout.write(" {:02x}".format(byte))
	#sys.stdout.write(" {:02x}\n".format(byte))


oneCount = 0
syncBits = 0 # at the beginning we are synced by definition

def encodeByte(byte, bitCount) :
	outString = ''
	#outString += '[bc={:d}]'.format(bitCount)
	global oneCount
	global syncBits
	#byte = byte << (8 - bitCount) // left align
	for i in range(bitCount) :
		bit = (byte & 0x01)
		byte = (byte >> 1) & 0xff
		# Manchester encode
		if bit : # 10
			outString += '10'
			if syncBits >= 8 : # bit stuffing after five one-bits
				oneCount += 1
				if oneCount >= 5 :
					outString += '01'
					oneCount = 0
			else :
				oneCount = 0
		else : # 01
			outString += '01'
			oneCount = 0
		syncBits += 1
	return outString


# Manchester encoding (according to G. E. Thomas' convention: 01 => 0, 10 => 1)
# with bit-stuffing (see 'SDLC' in https://en.wikipedia.org/wiki/Bit_stuffing)
# bit order is 'LSB first', sync-word (decoded) is 0x7E which is %0110101010101001 as unencoded raw value
# parameters:
#   telegram: string with '0' and '1'
def encodeTelegram(telegram) :
	global oneCount
	oneCount = 0
	global syncBits
	syncBits = 0
	outString = ''
	dataBits = 0 # at the beginning we are synced by definition
	firstLine = False # omit newline before first line
	byte = 0

	for i in telegram :
		if i == '|' or i == '\n' :
			if dataBits > 0 :
				outString += encodeByte(byte, dataBits)
			#if firstLine :
			#	firstLine = False
			#else :
			#	outString += '\n'
			outString += '|'
			dataBits = 0
			syncBits = 0
			oneCount = 0
			continue
		elif i == '1' :
			bit = 1
		elif i == '0' :
			bit = 0
		else :
			continue # ignore any unknown characters in the input stream

		byte = ((byte << 1) | bit) & 0xff
		dataBits += 1
		if dataBits >= 8 :
			outString += encodeByte(byte, 8)
			dataBits = 0

	if dataBits > 0 :
		outString += encodeByte(byte, dataBits)
	sys.stdout.write(outString)


# Manchester decoding (according to G. E. Thomas' convention: 01 => 0, 10 => 1)
# with bit-stuffing (see 'SDLC' in https://en.wikipedia.org/wiki/Bit_stuffing)
# bit order is 'LSB first', sync-word (decoded) is 0x7E which is %0110101010101001 as unencoded raw value
# parameters:
#   telegram: string with '0' and '1'
def decodeTelegram(telegram) :
	byte = [0x00, 0x00] # even and odd aligned interpretation
	byteSyncDetect = [0xff, 0xff] # differentiate between decoded unstuffed and original stream. Sync must be detected only in original stream
	oneCount = [0, 0]
	streamIdx = 0 # there are two streams: the 'even' and the 'odd'
	activeStream = -1 # the stream which is synced
	dataBits = 0 # number of data bits after the sync
	symbol = 0 # the current manchester symbol
	state = 1 # state machine: 0 = look for preamble (TODO: not implemented), 1 = look for sync word, 2 = synced / parse data
	firstLine = True # omit newline before first line
	for i in telegram :
		if i != '0' and i != '1' : # ignore any unknown characters in the input stream
			continue

		# Manchester decode, 'symbol' is always 2 bits of the raw data
		stuffed = False
		symbol = ((symbol << 1) | (1 if i == '1' else 0)) & 0x03
		if symbol == 1 : # "01"
			bit = 0
			if oneCount[streamIdx] == 5 :
				stuffed = True
			oneCount[streamIdx] = 0
		elif symbol == 2 : # "10"
			bit = 1
			oneCount[streamIdx] += 1
			if oneCount[streamIdx] > 6 :
				bit = -3; # error: illegal manchester value
		else :
			bit = -1; # error: illegal manchester value
			oneCount[streamIdx] = 0

		if bit < 0 :
			byte[streamIdx] = 0x00
			byteSyncDetect[streamIdx] = 0xff # this makes sure that the sync word is only detected when it really start with a 0
			if streamIdx == activeStream :
				activeStream = -1
				state = 1
		elif (state == 1) or (state == 2) :
			byteSyncDetect[streamIdx] = ((byteSyncDetect[streamIdx] >> 1) | (bit << 7)) & 0xff # bit order: LSB first
			if byteSyncDetect[streamIdx] == 0x7E:
				#print "Sync found at position {:d}".format(dataBits)
				state = 2 # sync found, parse data
				dataBits = 0
				activeStream = streamIdx
				if firstLine :
					firstLine = False
				else :
					sys.stdout.write("\n")
				printByte(byteSyncDetect[streamIdx])
				byte[streamIdx] = 0x00
				byteSyncDetect[streamIdx] = 0xff # this makes sure that the sync word is only detected when it really start with a 0
			elif (state == 2) and (activeStream == streamIdx):
				if not stuffed and oneCount[streamIdx] < 6 :
					byte[streamIdx] = ((byte[streamIdx] >> 1) | (bit << 7)) & 0xff # bit order: LSB first
					#byte[streamIdx] = ((byte[streamIdx] << 1) | bit) & 0xff # bit order: MSB first
					dataBits += 1
					if (dataBits % 8) == 0 :
						printByte(byte[streamIdx])
				#else :
					#print " [Stuffed bit found at position {:d}]".format(dataBits)

		#print " s{:d} syn{:02X} b{:02X} i{:s} bits{:03d} sym{:d} 1cnt{:03d} bit{:2d}".format(streamIdx, byteSyncDetect[streamIdx], byte[streamIdx], i, dataBits, symbol, oneCount[streamIdx], bit)
		streamIdx ^= 0x01 # toggle between odd and even stream interpretation

def usage() :
	print sys.argv[0], "d <data>"
	print "<data> is the raw bitstream captured e.g. with urh"


# Main
if len(sys.argv) >= 3 and sys.argv[1] == "d" :
	decodeTelegram(sys.argv[2])
	sys.stdout.write("\n")
elif len(sys.argv) >= 3 and sys.argv[1] == "e" :
	encodeTelegram(sys.argv[2])
	sys.stdout.write("\n")
else :
	usage()

import argparse
from asyncio import subprocess
import os
import platform
import socket
import threading
import netifaces
import signal
import sys
import concurrent.futures
import time
import subprocess

signal.signal(signal.SIGINT, lambda x, y: sys.exit(0))
parser = argparse.ArgumentParser(
    description='Network discovery tool that allows to know what ips are found in the specified network')
parser.add_argument('-nw', '--network', type=str,
                    help='Target network', default='')
parser.add_argument('-t', '--timeout', type=int,
                    help='Ping timeout (seconds)', default=1)
parser.add_argument('-s', '--slow',
                    help='Straight output, no thread joining', action='store_true')
parser.add_argument('-v', '--verbose',
                    help='Increase output verbosity', action='store_true')
args = parser.parse_args()
hostsList = []
threadsList = []
validTarget = False
MAX_HOST = 254


def promptNetworkInterfacesWindows():
    winCommand = 'ipconfig'
    ret = os.system(winCommand)


def promptNetworkInterfacesLinux():
    linCommand = 'ifconfig'
    iFaces2Display = []
    nOption = 1
    print('Displaying available interfaces')
    iFaces = socket.if_nameindex()
    print(iFaces)


def getTargetNetwork(interface):

    # For now it just returns the first three octets of the network interface ip
    # ToDo: Add MASK to determine true network address
    network = interface.split('.')
    network.pop()
    return network[0]+'.'+network[1]+'.'+network[2]


def parseSelectedIface(response, ifaces):
    found = False
    i = 0
    selection = None
    while (found == False and i < len(ifaces)):
        validValues = [str(ifaces[i]['index']), ifaces[i]
                       ['interface'], ifaces[i]['addr']]
        if (str(response) in validValues):
            found = True
            selection = i
        else:
            i += 1

    if (found == True):
        return getTargetNetwork(ifaces[selection]['addr'])
    else:
        return False


def promptConfirmation(parsedTargetNetwork):
    validConfirmation = False
    while (validConfirmation == False):
        selectedIfaceConfirm = input(
            'Perform scan on network %s: yes | no: ' % (parsedTargetNetwork))
        if (str(selectedIfaceConfirm).lower() == 'yes' or str(selectedIfaceConfirm).lower() == 'y' or selectedIfaceConfirm == ''):
            validTarget = True
            validConfirmation = True
            performPingSweep(parsedTargetNetwork)
        elif (str(selectedIfaceConfirm).lower() != 'no' and str(selectedIfaceConfirm).lower() != 'n'):
            print('Please use y/yes or n/no to confirm the selection')
        else:
            validConfirmation = True


def promptNetworkInterfaces():
    ifaces = []
    ifacesNames = netifaces.interfaces()
    while (validTarget == False):
        n = 0
        print('Available interfaces:')
        for i in ifacesNames:
            if (i != 'lo'):
                ip = netifaces.ifaddresses(i)[netifaces.AF_INET][0]['addr']
                ifaces.append({'index': n, 'interface': i, 'addr': ip})
                print('%s - %s: %s' % (n, i, ip))
                n += 1

        selectedIface = input('Select target network interface:')
        parsedTargetNetwork = parseSelectedIface(selectedIface, ifaces)
        if (parsedTargetNetwork != False):
            promptConfirmation(parsedTargetNetwork)
        else:
            print('No valid target selected')


def getCommand():
    print('Autodetecting current OS')
    osPlatform = platform.system()
    print('Detected OS: %s ' % (osPlatform))
    if (osPlatform.find('Windows') != -1):
        command = 'ping -n 1 -W '+str(args.timeout)
    elif (osPlatform.find('Linux') != -1):
        command = 'ping -c 1 -W '+str(args.timeout)
    else:
        print('No compatible OS detected')
    return command or False


def pingTarget(target, command):
    if args.verbose == True:
        print('Pinging %s' % target)

    resp = subprocess.run(command+' '+target, shell=True,
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    hostIsUp = resp.stdout.find(b'bytes from') != -1
    if (args.slow == False):
        if (hostIsUp == True):
            print('%s host is UP' % (target))
    else:
        if (hostIsUp == True):
            hostsList.append(target)
    if args.verbose == True:
        print('%s finished' % target)


def createThreads(targetNetwork, command):
    # Currently just looking for the 254 hosts (mask 255.255.255.0 (/24))
    # ToDo: calculate the real range of the number of hosts
    for ip in range(MAX_HOST):
        ping = threading.Thread(target=pingTarget, args=(
            targetNetwork+'.'+str(ip+1), command), daemon=True)
        ping.start()
        if (args.slow == True):
            ping.join()


def performPingSweep(targetNetwork):
    command = getCommand()
    if (command != False):
        startingTime = time.time()
        print('Starting ping sweep...')
        createThreads(targetNetwork, command)
        if (args.slow == True):
            getElapsedTime(startingTime)
            print('Discovered IPs: ')
            for h in hostsList:
                print(h)
    else:
        pass
    exit()


def getElapsedTime(startingTime):
    elapsedTime = time.time()-startingTime
    print('Scanning finished, elapsed time: %s' % (elapsedTime))


if __name__ == '__main__':
    if (args.slow == True and args.timeout <= 1):
        args.timeout = 3

    if (args.network == ''):
        print('No network defined!! A network will have to be selected from the system\'s Network Interfaces')
        promptNetworkInterfaces()

    else:
        print('Introduced network: %s' % (args.network))

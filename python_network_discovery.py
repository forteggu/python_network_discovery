import argparse
import os
import platform
import socket
import netifaces
parser = argparse.ArgumentParser(
    description='Network discovery tool that allows to know what ips are found in the specified network')
parser.add_argument('-nw', '--network', type=str,
                    help='Target network', default='')
args = parser.parse_args()


def promptNetworkInterfacesWindows():
    winCommand = 'ipconfig'
    ret = os.system(winCommand)


def promptNetworkInterfacesLinux():
    linCommand = 'ifconfig'
    iFaces2Display = []
    nOption = 1
    # ifaces=os.popen(linCommand)
    # process response
    print('Displaying available interfaces')
    # for line in ifaces.readlines():
    #print('Line: %s' %(line))
    # if(line.find('inet')!=-1):
    # iFaces2Display.append({'option':nOption,'iFace':line})
    # print(line)
    iFaces = socket.if_nameindex()
    print(iFaces)


def getTargetNetwork(interface):
    # Add MASK to determine true network address
    return True


def parseSelectedIface(response, ifaces):
    found = False
    i = 0
    selection = None
    # while (found == False and i < len(ifaces)):
    #    if (response == ifaces[i]['index'] or response==ifaces[i]['interface'] or response==ifaces[i]['addr']):
    #        found == True
    #        selection = i
    #    else:
    #        i += 1
    print(i)
    if (response == ifaces[i]['index'] or response == ifaces[i]['interface'] or response == ifaces[i]['addr']):
        print('VALID')

    if (found == True):
        print('Found i: %s' % selection)
        return getTargetNetwork(selection)
    else:
        print('I not found')
        return False


def promptNetworkInterfaces():
    ifaces = []
    ifacesNames = netifaces.interfaces()
    n = 0
    validTarget = False
    while (validTarget == False):
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
            selectedIfaceConfirm = input(
                'Perform scan on network %s: yes | no' % (parsedTargetNetwork))
            if (str(selectedIfaceConfirm).lower() == 'yes' or str(selectedIfaceConfirm).lower() == 'y'):
                validTarget = True
                performPing(parsedTargetNetwork)
        else:
            print('No valid target selected')


def performPing(targetNetwork):
    print('Autodetecting current OS')
    osPlatform = platform.system()
    print('Detected OS: %s ' % (osPlatform))
    if (osPlatform.find('Windows') != -1):
        promptNetworkInterfacesWindows()
        # search for interfaces
    elif (osPlatform.find('Linux') != -1):
        promptNetworkInterfacesLinux()
    else:
        print('No compatible OS detected')


def selectNetworkInterface():
    promptNetworkInterfaces()


if __name__ == '__main__':
    if (args.network == ''):
        print('No network defined!! A network will have to be selected from the system\'s Network Interfaces')
        selectNetworkInterface()

    else:
        print('Introduced network: %s' % (args.network))

import pprint
#from elementtree.ElementTree import ElementTree
from xml.etree.ElementTree import ElementTree

DeviceList = []

def extractDevices(Devices=None):
    for Device in Devices:
	print('The file has the following devices: %s:' %Device)
	DeviceList.append(Device)
	#print DeviceList

def extractTagData(DevicePart=None,searchtag=None):
    for tag in DevicePart.getchildren():
	if tag.tag==searchtag:
	    return tag.text

def extractDeviceParts(Device=None):
    for DevicePart in Device:
	print ('The device has the following parts: %s' %DevicePart)
	# a subpart is like the CPU of a generator and so forth
	for KeyAttribute in DevicePart.keys():
	    if DevicePart.get(KeyAttribute)=='generator':
		print 'hey we are dealing with a generator here:-)'
		#vendor
		vendor=extractTagData(DevicePart,'vendor')
		#model
		model=extractTagData(DevicePart,'model')
		# devicestate
		devicestate=extractTagData(DevicePart,'devicestate')

		return(vendor,model,devicestate)
		
	    elif DevicePart.get(KeyAttribute)=='lead':
		print 'hey we are dealing with a lead here'
		
	    else:
		print 'hey we are dealing with an unkown device part here. Please provide the XML file to the GNUmed team.'
		
def outputDeviceStatus(DeviceList=None):
    """ In this area GNUmed will place the status of all cardiac devices and device parts. 
    There can be more than one device at a time\n\n
    It potentially looks like this\n
    ----------------------------------------------------------------------------------------------------------------\n
    Device: SJM Atlas DR (active)     Battery: 2.4V (MOL)      Implanted:  Feb 09 2008\n\n
    RA: Medtronic Sprint fidelis (active, flaky, replacement)             Implanted: Feb 09 2008\n
    Sensing: 2 (1.5) mV    Threshold: 0.7/0.5 (1/0.4) V/ms       Impedance: 800 (900) Ohm\n\n
    RV: Medtronic Sprint fidelis (active, flaky, replacement)             Implanted: Feb 09 2008\n
    Sensing: 7 (15) mV    Threshold: 0.7/0.5 (1/0.4) V/ms       Impedance: 800 (900) Ohm\n\n
    LV: Medtronic Sprint fidelis (active, flaky, Y-connector)             Implanted: Feb 09 2008\n
    Sensing: 7 ( ?) mV    Threshold: 1/1.5 (1/1) V/ms       Impedance: 800 (900) Ohm\n
    ----------------------------------------------------------------------------------------------------------------\n
    Device: Medtronic Relia SR (inactive)     Battery 2.1V (EOL)   Implanted: Jan 23 2000\n\n
    Device: Medtronic Kappa SR (explanted)     Battery 2.1V (EOL)   Explanted: Jan 23 2000 (Jan 23 1995)\n
    -----------------------------------------------------------------------------------------------------------------\n
    RA Lead: Medtronic ? (inactive, capped)             Implanted: Jan 23 2000\n
    RV Lead: Medtronic ? (explanted)                        Explanted: Feb 09 2008
    """
    for Device in DeviceList:
        DeviceClass=Device.get("class")
        #parse the parts into a dictionary
	parts=extractDeviceParts(Device)
	print parts
        #DeviceManufacturer=
	#construct output for active settings dialog

if __name__ == '__main__':
    filename = 'GNUmed5.xml'
    tree = ElementTree(file='GNUmed6.xml')
    Devices = tree.getroot()
    extractDevices(Devices)
    outputDeviceStatus(DeviceList)
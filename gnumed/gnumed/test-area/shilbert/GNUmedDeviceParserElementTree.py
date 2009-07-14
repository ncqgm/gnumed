from lxml import etree

# DevicesList hold a list of all cardiac devices in the xml
# each list item holds a device context ( generator and one or more leads )
DevicesList = []
# DevicePartsList is the device context and holds one or more device parts. Each list item
# is a cardiac device part such as lead , generator which in turn can consist of 
# device parts such as mainboard or battery
DevicePartsList = []

def extractDevices(DevicesTree=None):
    for Device in DevicesTree:
	#DeviceClass=CardiacDevice.get("class")
	#print DeviceClass
	DevicesList.append(Device)
    return DevicesList

def extractDeviceParts(Device=None):
    for DevicePart in Device:
	DevicePartsList.append(DevicePart)
    return DevicePartsList

def extractDevicePartSpecs(DevicePart=None):
    DevicePartSpecsList=[]
    KeyAttributes = DevicePart.keys()
    for KeyAttribute in KeyAttributes:
	if DevicePart.get(KeyAttribute)=='generator':
    	    print 'hey we are dealing with a generator here:-)'
    	    #vendor
	    vendor=extractTagData(DevicePart,'vendor')
    	    DevicePartSpecsList.append(vendor)
	    #model
	    model=extractTagData(DevicePart,'model')
    	    DevicePartSpecsList.append(model)
    	    # devicestate
    	    devicestate=extractTagData(DevicePart,'devicestate')
    	    DevicePartSpecsList.append(devicestate)
        
    	    return DevicePartSpecsList
        
	elif DevicePart.get(KeyAttribute)=='lead':
    	    print 'hey we have a lead here'
    	    return DevicePartSpecsList
	else:
    	    print 'hey we have an unkown device here. Please provide the XML file to the GNUmed team.'
    	    return DevicePartSpecsList
	
def extractDeviceSubParts(Device=None):
    DeviceObject = Device[0]
    for DevicePart in DeviceObject:
        print ('The device has the following parts: %s' %DevicePart)
        # a subpart is like the CPU of a generator and so forth
        for KeyAttribute in DevicePart.keys():
            if DevicePart.get(KeyAttribute)=='mainboard':
                print 'hey we are dealing with a mainboard here:-)'
                #manufacturer
                manufacturer=extractTagData(DevicePart,'manufacturer')
                #model
                model=extractTagData(DevicePart,'model')
                #return(manufacturer,model)

            elif DevicePart.get(KeyAttribute)=='battery':
                print 'hey we are dealing with a battery here'

            else:
                print 'hey we are dealing with an unkown device part here. Please provide the XML file to the GNUmed team.'

def extractTagData(DevicePart=None,searchtag=None):
    for tag in DevicePart.getchildren():
        if tag.tag==searchtag:
            return tag.text
        
def outputDeviceStatus(tree=None):
    DevicesDict = {}
    DevicePartSpecsDict = {}
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
    DevicesTree = tree.getroot()
    DevicesList = extractDevices(DevicesTree)
    print 'Number of devices: %s' %len(DevicesList)
    
    for Device in DevicesList:
	# parse for generator and leads
	DevicePartsList = extractDeviceParts(Device)
    print DevicePartsList
    
    # get subparts and specs for each device part ()
    for DevicePart in DevicePartsList:
	DevicePartSpecsList = extractDevicePartSpecs(DevicePart)
	print DevicePartSpecsList
	# get parent element for grouping of devices
	DevicePartParent = DevicePart.getparent()
	DevicePartSpecsDict[DevicePartParent] = DevicePartSpecsList
	print DevicePartSpecsDict

if __name__ == '__main__':
    # for now assume that the xml file provide the cardiac device context.
    # that pretty much means logical connection of leads and generator is provided in the xml
    tree = etree.parse('GNUmed6.xml')
    outputDeviceStatus(tree)

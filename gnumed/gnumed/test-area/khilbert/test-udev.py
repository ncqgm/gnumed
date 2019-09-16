#!/usr/bin/python3

import sys
import shutil

import pyudev
import psutil

def enumerate_removable_partitions():
	removable_partitions = {}
	ctxt = pyudev.Context()
	removable_devices = [ dev for dev in ctxt.list_devices(subsystem='block', DEVTYPE='disk') if dev.attributes.get('removable') == b'1' ]
	all_mounted_partitions = { part.device: part for part in psutil.disk_partitions() }
	for device in removable_devices:
		partitions_on_removable_device = {
			part.device_node: {
				'type': device.properties['ID_TYPE'],
				'bus': device.properties['ID_BUS'],
				'device': part.properties['DEVNAME'],
				'vendor': part.properties['ID_VENDOR'],
				'model': part.properties['ID_MODEL'],
				'fs_label': part.properties['ID_FS_LABEL'],
				'is_mounted': False,
				'mountpoint': None,
				'fs_type': None,
				'size_in_bytes': -1,
				'bytes_free': 0
			} for part in ctxt.list_devices(subsystem='block', DEVTYPE='partition', parent=device)
		}
		for part in partitions_on_removable_device:
			try:
				partitions_on_removable_device[part]['mountpoint'] = all_mounted_partitions[part].mountpoint
				partitions_on_removable_device[part]['is_mounted'] = True
				partitions_on_removable_device[part]['fs_type'] = all_mounted_partitions[part].fstype
				du = shutil.disk_usage(all_mounted_partitions[part].mountpoint)
				partitions_on_removable_device[part]['size_in_bytes'] = du.total
				partitions_on_removable_device[part]['bytes_free'] = du.free
			except KeyError:
				pass			# not mounted
		removable_partitions.update(partitions_on_removable_device)
	return removable_partitions


def enumerate_optical_writers():
	optical_writers = []
	ctxt = pyudev.Context()
	for dev in [ dev for dev in ctxt.list_devices(subsystem='block', DEVTYPE='disk') if dev.properties.get('ID_CDROM_CD_RW', None) == '1' ]:
		optical_writers.append ({
			'type': dev.properties['ID_TYPE'],
			'bus': dev.properties['ID_BUS'],
			'device': dev.properties['DEVNAME'],
			'model': dev.properties['ID_MODEL']
		})
	return optical_writers


ctxt = pyudev.Context()
for dev in ctxt.list_devices(subsystem='block', DEVTYPE='disk'):# if dev.attributes.get('removable') == b'1':
	for a in dev.attributes.available_attributes:
		print(a, dev.attributes.get(a))
#	for key, value in dev.attributes:
#		print('{key}={value}'.format(key=key, value=value))
	for key, value in dev.items():
		print('{key}={value}'.format(key=key, value=value))
	print('---------------------------')

sys.exit()

for writer in enumerate_optical_writers():
	print('%s@%s: %s @ %s' % (
		writer['type'],
		writer['bus'],
		writer['model'],
		writer['device']
	))

#	for key, value in dev.items():
#		print('{key}={value}'.format(key=key, value=value))
#	print('---------------------------')

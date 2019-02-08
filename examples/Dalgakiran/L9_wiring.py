from connio.rest import Client
from connio.rest.api.v3.account.propertyy import PropertyInstance
from connio.rest.api.v3.account.method import MethodInstance

from L9 import *

def wire(client):
    # Create Logika L9 profile
    compressor = client.account.deviceprofiles.create(name='LogikaL9', 
                                                  friendly_name='Logika L9 Controller',
                                                  base_profile='BaseLogikaProfile',
                                                  description='Logika L9 controller',
                                                  tags=['logika', 'L9'],
                                                  device_class='controller',
                                                  product_name='L9',
                                                  vendor_name='Logika'
                                                )

    #------ Add profile methods

    accessLevel2 = 'private'

    client.account.methods(compressor.id).create(name='fetchAlarmList', method_impl= MethodInstance.MethodImplementation(fetchAlarmList_body()), access_type=accessLevel2)
    client.account.methods(compressor.id).create(name='fetchReadRequest', method_impl= MethodInstance.MethodImplementation(fetchReadRequest_body()), access_type=accessLevel2)
    client.account.methods(compressor.id).create(name='fetchWriteRequest', method_impl= MethodInstance.MethodImplementation(fetchWriteRequest_body()), access_type=accessLevel2)
    client.account.methods(compressor.id).create(name='fetchModbusSettings', method_impl= MethodInstance.MethodImplementation(fetchModbusSettings_body()), access_type=accessLevel2)
    client.account.methods(compressor.id).create(name='fetchControllerStates', method_impl= MethodInstance.MethodImplementation(fetchControllerStates_body()), access_type=accessLevel2)
    client.account.methods(compressor.id).create(name='fetchCompressorStates', method_impl= MethodInstance.MethodImplementation(fetchCompressorStates_body()), access_type=accessLevel2)
    client.account.methods(compressor.id).create(name='fetchCompressorStateTypes', method_impl= MethodInstance.MethodImplementation(fetchCompressorStateTypes_body()), access_type=accessLevel2)

    accessLevel3 = 'private'

    # Controller specific tag R/W operations

    accessLevel4 = 'public'

    client.account.methods(compressor.id).create(name='sendCommand', method_impl= MethodInstance.MethodImplementation(sendCommand_body()), access_type=accessLevel4)
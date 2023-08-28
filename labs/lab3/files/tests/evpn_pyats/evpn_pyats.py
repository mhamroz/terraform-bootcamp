'''
evpn_pyats.py

'''
# see https://pubhub.devnetcloud.com/media/pyats/docs/aetest/index.html
# for documentation on pyATS test scripts

# optional author information
# (update below with your contact information if needed)
__author__ = 'Cisco Systems Inc.'
__copyright__ = 'Copyright (c) 2019, Cisco Systems Inc.'
__contact__ = ['pyats-support-ext@cisco.com']
__credits__ = ['list', 'of', 'credit']
__version__ = 1.0

import logging

from pyats import aetest

import re

# create a logger for this module
logger = logging.getLogger(__name__)

class CommonSetup(aetest.CommonSetup):

    @aetest.subsection
    def connect(self, testbed):
        '''
        establishes connection to all your testbed devices.
        '''
        # make sure testbed is provided
        assert testbed, 'Testbed is not provided!'

        # connect to all testbed devices
        testbed.connect()


class ospf_connectivity(aetest.Testcase):
    '''ospf_connectivity

    Check if all OSPF neigbhor relationships are in FULL state

    '''

    # testcase groups (uncomment to use)
    # groups = []

    @aetest.setup
    def setup(self,testbed):
        self.data = {}
        for name,device in testbed.devices.items():
            self.data[name] = device.learn('ospf').to_dict() 
        pass
    # you may have N tests within each testcase
    # as long as each bears a unique method name
    # this is just an example
    @aetest.test
    def check_ospf_neighbors(self,testbed):
        for name,device in testbed.devices.items():
            ospf_int = self.data[name]['info']['vrf']['default']['address_family']['ipv4']['instance']['1']['areas']['0.0.0.0']['interfaces']
            for k1,v1 in ospf_int.items():
                neighbors = v1.get('neigbhors')
                if isinstance(neighbors,dict):
                    for k2,v2 in neighbors.items():
                        state = v2['state']
                        assert state == 'full', "neighbor not in full state"      

    @aetest.cleanup
    def cleanup(self):
        pass
    

class bgp_connectivity(aetest.Testcase):
    '''bgp_connectivity

    Check if BGP neighbors are in Established state

    '''

    # testcase groups (uncomment to use)
    # groups = []

    @aetest.setup
    def setup(self,testbed):
        self.data = {}
        for name,device in testbed.devices.items():
            self.data[name] = device.parse('show bgp l2vpn evpn summary')
        pass


    # you may have N tests within each testcase
    # as long as each bears a unique method name
    # this is just an example
    @aetest.test
    def check_bgp_neighbors(self,testbed):
        for name,device in testbed.devices.items():
            neighbor = self.data[name]['vrf']['default']['neighbor']
            for k1,v1 in neighbor.items():
                try:
                    to_int = int(v1['address_family']['']['state_pfxrcd'])
                except:
                    to_int = 0
                assert to_int > 0, f"neighbor {k1} not in established state"

    @aetest.cleanup
    def cleanup(self):
        pass
    

class nve_peers_connectivity(aetest.Testcase):
    '''nve_peers_connectivity

    Check if NVE peer is in UP state
    '''

    # testcase groups (uncomment to use)
    # groups = []

    @aetest.setup
    def setup(self,testbed):
        self.data = {}
        for name,device in testbed.devices.items():
            self.data[name] = device.execute('show nve peers')
        pass


    # you may have N tests within each testcase
    # as long as each bears a unique method name
    # this is just an example
    @aetest.test
    def check_nve_peers(self,testbed):
        rex = re.compile(r'(\w+)\s+\d+\s+\w+\s+(\d+\.\d+\.\d+\.\d+)\s+\d+\s+\d+\s+(\w+)')
        for name,device in testbed.devices.items():
            w = rex.findall(self.data[name])
            if 'spine' not in name:
                if len(w) > 0:
                    assert w[0][2] == 'UP', f"NVE peer not in up state"


    @aetest.cleanup
    def cleanup(self):
        pass

class CommonCleanup(aetest.CommonCleanup):
    '''CommonCleanup Section

    < common cleanup docstring >

    '''

    # uncomment to add new subsections
    # @aetest.subsection
    # def subsection_cleanup_one(self):
    #     pass

if __name__ == '__main__':
    # for stand-alone execution
    import argparse
    from pyats import topology

    parser = argparse.ArgumentParser(description = "standalone parser")
    parser.add_argument('--testbed', dest = 'testbed',
                        help = 'testbed YAML file',
                        type = topology.loader.load,
                        default = None)

    # do the parsing
    args = parser.parse_known_args()[0]

    aetest.main(testbed = args.testbed)
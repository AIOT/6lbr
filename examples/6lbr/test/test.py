#!/usr/bin/python2.7

import unittest
import sys
from os import system
from subprocess import Popen
from time import sleep
import config
from support import *
from tcpdump import TcpDump
import time

def skipUnlessTrue(descriptor):
    if not hasattr(config, descriptor):
        return unittest.skip("%s not defined in config.py, skipping" % descriptor)
    if getattr(config, descriptor) == 0:
        return unittest.skip("%s set to False in config.py, skipping" % descriptor)
    else:
        return lambda func: func

def repeat(times):
    def repeatHelper(f):
        def callHelper(*args):
            for i in range(0, times):
                f(*args)
        return callHelper
    return repeatHelper

class TestSupport:
    br=config.br
    wsn=config.wsn
    platform=config.platform
    tcpdump=TcpDump()
    ip_6lbr=None
    ip_host=None
    ip_mote="aaaa::" + config.iid_mote

    def setUp(self):
        print >> sys.stderr, "\n---\n"
        self.platform.setUp()
        self.br.setUp()
        self.wsn.setUp()
        ip = self.wsn.get_mote_ip()
        if ip != '':
            self.ip_mote = ip

    def tearDown(self):
        self.wsn.tearDown()
        self.br.tearDown()
        self.platform.tearDown()

    def set_mode(self, mode, ra_daemon=False, accept_ra=False):
        return self.br.set_mode(mode, config.channel, ra_daemon, accept_ra)

    def start_ra(self, itf):
        return self.platform.start_ra(itf)

    def stop_ra(self):
        return self.platform.stop_ra()

    def start_6lbr(self, log):
        return self.br.start_6lbr(log)

    def stop_6lbr(self):
        return self.br.stop_6lbr()

    def start_mote(self):
        return self.wsn.start_mote(config.channel)

    def stop_mote(self):
        return self.wsn.stop_mote()

    def ping(self, target):
        return self.platform.ping(target)

    def wait_mote_in_6lbr(self, count):
        return True

    def wait_ping(self, count, target):
        for n in range(count):
            if (self.ping(target)):
                return True
        return False

    def ping_6lbr(self):
        return self.ping( self.ip_6lbr )

    def wait_ping_6lbr(self, count):
        return self.wait_ping( count, self.ip_6lbr )

    def ping_mote(self):
        return self.ping( self.ip_mote )

    def wait_ping_mote(self, count):
        print("Pinging mote %s" % self.ip_mote)
        return self.wait_ping( count, self.ip_mote )

    def ping_from_mote(self, address, expect_reply=False, count=0):
        return self.wsn.ping( address, expect_reply, count )

class TestScenarios:
    def log_file(self, log_name):
        return "%s_%s.log" % (log_name, self.__class__.__name__)

    @skipUnlessTrue("S0")
    def test_S0(self):
        """
        Check 6LBR start-up and connectivity
        """
        print >> sys.stderr, "******** Test S00 ********"
        timestart = time.time()
        self.assertTrue(self.support.start_6lbr(self.log_file('test_S0')), "Could not start 6LBR")
        self.set_up_network()
        self.assertTrue(self.support.wait_ping_6lbr(40), "6LBR is not responding")
        self.tear_down_network()
        self.assertTrue(self.support.stop_6lbr(), "Could not stop 6LBR")
        timestop = time.time()
	print >> sys.stderr, "Test duration = %f s" % (timestop-timestart,)

    @skipUnlessTrue("S1")
    def test_S1(self):
        """
        Ping from the computer to the mote when the PC knows the BR but the BR does not know the
        mote.
        """
        print >> sys.stderr, "******** Test S01 ********"
        timestart = time.time()
        self.assertTrue(self.support.start_6lbr(self.log_file('test_S1')), "Could not start 6LBR")
        self.set_up_network()
        self.assertTrue(self.support.start_mote(), "Could not start up mote")
        self.assertTrue(self.support.wait_mote_in_6lbr(30), "Mote not detected")
        self.assertTrue(self.support.wait_ping_mote(60), "Mote is not responding")
        self.assertTrue(self.support.stop_mote(), "Could not stop mote")
        self.tear_down_network()
        self.assertTrue(self.support.stop_6lbr(), "Could not stop 6LBR")
        timestop = time.time()
	print >> sys.stderr, "Test duration = %f s" % (timestop-timestart,)

    @skipUnlessTrue("S2")
    def test_S2(self):
        """
        Ping from the computer to the mote when the PC does not know the BR and the BR knows
        the mote.
        """
        print >> sys.stderr, "******** Test S02 ********"
        timestart = time.time()
        self.assertTrue(self.support.start_6lbr(self.log_file('test_S2')), "Could not start 6LBR")
        self.assertTrue(self.support.start_mote(), "Could not start up mote")
        self.assertTrue(self.support.wait_mote_in_6lbr(30), "Mote not detected")
        self.set_up_network()
        self.assertTrue(self.support.wait_ping_mote(60), "Mote is not responding")
        self.assertTrue(self.support.stop_mote(), "Could not stop mote")
        self.tear_down_network()
        self.assertTrue(self.support.stop_6lbr(), "Could not stop 6LBR")
        timestop = time.time()
	print >> sys.stderr, "Test duration = %f s" % (timestop-timestart,)

    @skipUnlessTrue("S3")
    def test_S3(self):
        """
        Ping from the computer to the mote when everyone is known but the mote has been disconnected.
        """
        print >> sys.stderr, "******** Test S03 ********"
        self.assertTrue(self.support.start_6lbr(self.log_file('test_S3')), "Could not start 6LBR")
        self.assertTrue(self.support.start_mote(), "Could not start up mote")
        self.assertTrue(self.support.wait_mote_in_6lbr(30), "Mote not detected")
        self.set_up_network()
        self.assertTrue(self.support.wait_ping_mote(60), "Mote is not responding")
        self.assertTrue(self.support.stop_mote(), "Could not stop mote")
        self.assertFalse(self.support.wait_ping_mote(10), "Mote is still responding")
        self.tear_down_network()
        self.assertTrue(self.support.stop_6lbr(), "Could not stop 6LBR")

    @skipUnlessTrue("S4")
    def test_S4(self):
        """
        Starting from a stable RPL topology, restart the border router and observe how it attaches
        to the RPL DODAG.
        """
        print >> sys.stderr, "******** Test S04 ********"
        self.assertTrue(self.support.start_6lbr(self.log_file('test_S4_a')), "Could not start 6LBR")
        self.assertTrue(self.support.start_mote(), "Could not start up mote")
        self.assertTrue(self.support.wait_mote_in_6lbr(30), "Mote not detected")
        self.set_up_network()
        self.assertTrue(self.support.wait_ping_mote(60), "Mote is not responding")
        self.tear_down_network()
        self.assertTrue(self.support.stop_6lbr(), "Could not stop 6LBR")
        self.assertTrue(self.support.start_6lbr(self.log_file('test_S4_b')), "Could not start 6LBR")
        self.set_up_network()
        self.assertTrue(self.support.wait_ping_mote(60), "Mote is not responding")
        self.assertTrue(self.support.stop_mote(), "Could not stop mote")
        self.tear_down_network()
        self.assertTrue(self.support.stop_6lbr(), "Could not stop 6LBR")

    @skipUnlessTrue("S5")
    def test_S5(self):
        """
        Wait for a DAD between the computer and the BR, then disconnect and reconnect the com-
        puter and observe the reaction of the BR to a computer's DAD.
        """
        print >> sys.stderr, "******** Test S05 ********"
        pass

    @skipUnlessTrue("S6")
    def test_S6(self):
        """
        Observe the NUDs between the computer and the BR.
        """
        print >> sys.stderr, "******** Test S06 ********"
        pass

    @skipUnlessTrue("S7")
    def test_S7(self):
        """
        Test the Auconfiguration process of the BR in bridge mode and observe its ability to take a
        router prefix (by using the computer as a router), and deal with new RA once configured.
        """
        print >> sys.stderr, "******** Test S07 ********"
        pass

    @skipUnlessTrue("S8")
    def test_S8(self):
        """
        Observe the propagation of the RIO in the WSN side (when supported in the WPAN).
        """
        print >> sys.stderr, "******** Test S08 ********"
        pass

    @skipUnlessTrue("S9")
    def test_S9(self):
        """
        Test the using of the default router.
        """
        print >> sys.stderr, "******** Test S09 ********"
        pass

    @skipUnlessTrue("S10")
    def test_S10(self):
        """
        Ping from the sensor to the computer when the sensor does not know the CBR.
        """
        print >> sys.stderr, "******** Test S10 ********"
        pass

    @skipUnlessTrue("S11")
    def test_S11(self):
        """
        Ping from the sensor to the computer when the CBR does not know the computer.
        """
        print >> sys.stderr, "******** Test S11 ********"
        self.assertTrue(self.support.start_6lbr(self.log_file('test_S11')), "Could not start 6LBR")
        self.set_up_network()
        self.assertTrue(self.support.start_mote(), "Could not start up mote")
        self.assertTrue(self.support.wait_mote_in_6lbr(30), "Mote not detected")
        self.assertTrue(self.support.wait_ping_mote(60), "Mote is not responding")
        self.assertTrue(self.support.ping_from_mote(self.support.ip_host, True, 60), "Host is not responding")
        self.assertTrue(self.support.stop_mote(), "Could not stop mote")
        self.tear_down_network()
        self.assertTrue(self.support.stop_6lbr(), "Could not stop 6LBR")

    @skipUnlessTrue("S12")
    def test_S12(self):
        """
        Ping from the sensor to an external domain (as the inet address of google.com) and
        observe all the sending process.
        """
        print >> sys.stderr, "******** Test S12 ********"
        self.assertTrue(self.support.start_6lbr(self.log_file('test_S11')), "Could not start 6LBR")
        self.set_up_network()
        self.assertTrue(self.support.start_mote(), "Could not start up mote")
        self.assertTrue(self.support.wait_mote_in_6lbr(30), "Mote not detected")
        self.assertTrue(self.support.wait_ping_mote(60), "Mote is not responding")
        if self.__class__.__name__ == 'SmartBridgeAuto':
            self.assertTrue(self.support.tcpdump.expect_ping_request(self.support.br.itf, "cccc::1", 30, bg=True), "")
        else:
            self.assertTrue(self.support.tcpdump.expect_ns(self.support.br.itf, [0xbbbb, 0, 0, 0, 0, 0, 0, 1], 30, bg=True), "")
        self.assertTrue(self.support.ping_from_mote("cccc::1"), "")
        self.assertTrue(self.support.tcpdump.check_result(), "")
        self.assertTrue(self.support.stop_mote(), "Could not stop mote")
        self.tear_down_network()
        self.assertTrue(self.support.stop_6lbr(), "Could not stop 6LBR")

@skipUnlessTrue("mode_SmartBridgeManual")
class SmartBridgeManual(unittest.TestCase,TestScenarios):
    def setUp(self):
        self.support=TestSupport()
        self.support.ip_6lbr='aaaa::' + config.iid_6lbr
        self.support.ip_host='aaaa::200'
        self.support.setUp()
        self.support.set_mode('SMART-BRIDGE', accept_ra=False)

    def tearDown(self):
        self.tear_down_network()
        self.support.tearDown()

    def set_up_network(self):
        sleep(2)
        self.assertTrue( self.support.platform.configure_if(self.support.br.itf, self.support.ip_host), "")

    def tear_down_network(self):
        self.assertTrue( self.support.platform.unconfigure_if(self.support.br.itf, self.support.ip_host), "")

@skipUnlessTrue("mode_SmartBridgeAuto")
class SmartBridgeAuto(unittest.TestCase,TestScenarios):
    def setUp(self):
        self.support=TestSupport()
        self.support.ip_6lbr='aaaa::' + config.iid_6lbr
        self.support.ip_host='aaaa::200'
        self.support.setUp()
        self.support.set_mode('SMART-BRIDGE', accept_ra=True)

    def tearDown(self):
        self.support.tearDown()

    def set_up_network(self):
        sleep(2)
        #self.support.platform.accept_ra(self.support.br.itf)
        self.assertTrue( self.support.platform.configure_if(self.support.br.itf, self.support.ip_host), "")
        self.assertTrue( self.support.start_ra(self.support.br.itf), "")

    def tear_down_network(self):
        self.assertTrue( self.support.stop_ra(), "")

@skipUnlessTrue("mode_Router")
class Router(unittest.TestCase,TestScenarios):
    def setUp(self):
        self.support=TestSupport()
        self.support.ip_6lbr='bbbb::100'
        self.support.setUp()
        self.support.set_mode('ROUTER', ra_daemon=True)

    def tearDown(self):
        self.support.tearDown()
        
    def set_up_network(self):
        sleep(10)
        self.assertTrue(self.support.platform.accept_ra(self.support.br.itf), "Could not enable RA configuration support")
        if self.support.platform.support_rio():
            self.assertTrue(self.support.platform.accept_rio(self.support.br.itf), "Could not enable RIO support")
        self.assertTrue(self.support.tcpdump.expect_ra(self.support.br.itf, 30), "")
        self.assertTrue(self.support.platform.check_prefix(self.support.br.itf, 'bbbb:'), "Interface not configured")
        self.support.ip_host=self.support.platform.get_address_with_prefix(self.support.br.itf, 'bbbb:')
        if not self.support.platform.support_rio():
            self.assertTrue(self.support.platform.add_route("aaaa::", gw=self.support.ip_6lbr), "Could not add route")

    def tear_down_network(self):
        if not self.support.platform.support_rio():
            self.assertTrue(self.support.platform.rm_route("aaaa::", gw=self.support.ip_6lbr), "Could not remove route")

@skipUnlessTrue("mode_RouterNoRa")
class RouterNoRa(unittest.TestCase,TestScenarios):
    def setUp(self):
        self.support=TestSupport()
        self.support.ip_6lbr='bbbb::100'
        self.support.ip_host='bbbb::200'
        self.support.setUp()
        self.support.set_mode('ROUTER', ra_daemon=False)

    def tearDown(self):
        self.support.tearDown()

    def set_up_network(self):
        sleep(2)
        self.assertTrue( self.support.platform.configure_if(self.support.br.itf, self.support.ip_host), "")
        self.assertTrue( self.support.platform.add_route("aaaa::", gw=self.support.ip_6lbr), "")

    def tear_down_network(self):
        self.assertTrue( self.support.platform.rm_route("aaaa::", gw=self.support.ip_6lbr), "")
        self.assertTrue( self.support.platform.unconfigure_if(self.support.br.itf, self.support.ip_host), "")


def main():
    for i in range(1,config.test_repeat+1):
        print >> sys.stderr, " ============"
        print >> sys.stderr, " == RUN %d ==" % (i,)
        unittest.main(exit=False)

if __name__ == '__main__':
    main()

'''
Description: This test will verify that ONOS continues to work as instances 
of ONOS core are shut down. If one instance goes down, it is expected that the 
switches assigned to that controller (and have backup controllers assigned)
will be reassigned to one of the backup switches. At this time, one caveat is 
that the ONOS controller that is taken down must be one on which the intents are
not installed.
'''
class HATestONOSFC1:

    def __init__(self) :
        self.default = ''

    '''
    CASE1 is to close any existing instances of ONOS, clean out the 
    RAMCloud database, and start up ONOS instances. 
    '''
    def CASE1(self,main) :
        import time
        main.log.report("Initial cleanup and startup")
        main.case("Initial Startup")
        main.step("Stop ONOS")
        main.ONOS1.stop_all()
        main.ONOS2.stop_all()
        main.ONOS3.stop_all()
        main.ONOS4.stop_all()
        main.ONOS5.stop_all()
        main.ONOS1.stop_rest()
        main.ONOS2.stop_rest()
        main.ONOS3.stop_rest()
        main.ONOS4.stop_rest()
        main.ONOS5.stop_rest()

        main.step("Checking git commit")
        ONOS_commit = []
        ONOS_commit.append(main.ONOS1.get_branch())
        ONOS_commit.append(main.ONOS2.get_branch())
        ONOS_commit.append(main.ONOS3.get_branch())
        ONOS_commit.append(main.ONOS4.get_branch())
        ONOS_commit.append(main.ONOS5.get_branch())
        #Compare commits and if different print them all out
        if len(set(ONOS_commit)) == 1:
            main.log.report("On branch: "+ ONOS_commit[0])
        else:
            main.log.report("Warning, ONOS VM's on different commits")
            main.log.report("ONOS1 is on branch: "+ ONOS_commit[0])
            main.log.report("ONOS2 is on branch: "+ ONOS_commit[1])
            main.log.report("ONOS3 is on branch: "+ ONOS_commit[2])
            main.log.report("ONOS4 is on branch: "+ ONOS_commit[3])
            main.log.report("ONOS5 is on branch: "+ ONOS_commit[4])

        main.step("Startup Zookeeper")
        main.ZK1.start()
        main.ZK2.start()
        main.ZK3.start()
        main.ZK4.start()
        main.ZK5.start()
        time.sleep(2)
        ZK_Status = main.ZK1.isup() and main.ZK2.isup()\
                and main.ZK3.isup() and main.ZK4.isup() and main.ZK5.isup()
        utilities.assert_equals(expect=main.TRUE,actual=ZK_Status ,
                onpass="Zookeeper started successfully",onfail="ZOOKEEPER FAILED TO START")
        main.step("Cleaning RC Database and Starting All")
        main.RC1.del_db()
        main.RC2.del_db()
        main.RC3.del_db()
        main.RC4.del_db()
        main.RC5.del_db()
        main.ONOS1.start_all()
        main.ONOS2.start_all()
        main.ONOS3.start_all()
        main.ONOS4.start_all()
        main.ONOS5.start_all()
        main.ONOS1.start_rest()
        main.step("Testing Startup")
        vm1 = main.RC1.status_coor and main.RC1.status_serv and \
                main.ONOS1.isup()
        vm2 = main.RC2.status_coor and main.ONOS2.isup()
        vm3 = main.RC3.status_coor and main.ONOS3.isup()
        vm4 = main.RC4.status_coor and main.ONOS4.isup()
        vm5 = main.RC5.status_coor and main.ONOS5.isup()
        result = ZK_Status and vm1 and vm2 and vm3 and vm4 and vm5
        if result == main.TRUE:
            main.log.report("All components started successfully")
        utilities.assert_equals(expect=main.TRUE,actual=result,
                onpass="All components started successfully",
                onfail="One or more components failed to start")
        #if result==main.FALSE:
        #    main.cleanup()
        #    main.exit()

    '''
    CASE2
    '''
    def CASE2(self,main) :
        import time
        import json
        import re

        ONOS1_ip = main.params['CTRL']['ip1']
        ONOS2_ip = main.params['CTRL']['ip2']
        ONOS3_ip = main.params['CTRL']['ip3']
        ONOS4_ip = main.params['CTRL']['ip4']
        ONOS5_ip = main.params['CTRL']['ip5']

        ONOS1_port = main.params['CTRL']['port1']
        ONOS2_port = main.params['CTRL']['port2']
        ONOS3_port = main.params['CTRL']['port3']
        ONOS4_port = main.params['CTRL']['port4']
        ONOS5_port = main.params['CTRL']['port5']

        main.log.report("Assigning switches to controllers")
        main.case("Assigning Controllers")
        main.step("Assign Master Controllers")
        for i in range(1,29):
            if i ==1:
                main.Mininet1.assign_sw_controller(sw=str(i),ip1=ONOS1_ip,port1=ONOS1_port)
            elif i>=2 and i<5:
                main.Mininet1.assign_sw_controller(sw=str(i),ip1=ONOS2_ip,port1=ONOS2_port)
            elif i>=5 and i<8:
                main.Mininet1.assign_sw_controller(sw=str(i),ip1=ONOS3_ip,port1=ONOS3_port)
            elif i>=8 and i<18:
                main.Mininet1.assign_sw_controller(sw=str(i),ip1=ONOS4_ip,port1=ONOS4_port)
            elif i>=18 and i<28:
                main.Mininet1.assign_sw_controller(sw=str(i),ip1=ONOS5_ip,port1=ONOS5_port)
            else:
                main.Mininet1.assign_sw_controller(sw=str(i),ip1=ONOS1_ip,port1=ONOS1_port)
        
        Switch_Mastership = main.TRUE
        for i in range (1,29):
            if i==1:
                response = main.Mininet1.get_sw_controller("s"+str(i))
                print("Response is " + str(response))
                if re.search("tcp:"+ONOS1_ip,response):
                    Switch_Mastership = Switch_Mastership and main.TRUE
                else:
                    Switch_Mastership = main.FALSE
            elif i>=2 and i<5:
                response = main.Mininet1.get_sw_controller("s"+str(i))
                print("Response is " + str(response))
                if re.search("tcp:"+ONOS2_ip,response):
                    Switch_Mastership = Switch_Mastership and main.TRUE
                else:
                    Switch_Mastership = main.FALSE
            elif i>=5 and i<8:
                response = main.Mininet1.get_sw_controller("s"+str(i))
                print("Response is " + str(response))
                if re.search("tcp:"+ONOS3_ip,response):
                    Switch_Mastership = Switch_Mastership and main.TRUE
                else:
                    Switch_Mastership = main.FALSE
            elif i>=8 and i<18:
                response = main.Mininet1.get_sw_controller("s"+str(i))
                print("Response is " + str(response))
                if re.search("tcp:"+ONOS4_ip,response):
                    Switch_Mastership = Switch_Mastership and main.TRUE
                else:
                    Switch_Mastership = main.FALSE
            elif i>=18 and i<28:
                response = main.Mininet1.get_sw_controller("s"+str(i))
                print("Response is " + str(response))
                if re.search("tcp:"+ONOS5_ip,response):
                    Switch_Mastership = Switch_Mastership and main.TRUE
                else:
                    Switch_Mastership = main.FALSE
            else:
                response = main.Mininet1.get_sw_controller("s"+str(i))
                print("Response is" + str(response))
                if re.search("tcp:" +ONOS1_ip,response):
                    Switch_Mastership = Switch_Mastership and main.TRUE
                else:
                    Switch_Mastership = main.FALSE
        if Switch_Mastership == main.TRUE:
            main.log.report("MasterControllers assigned correctly")
        utilities.assert_equals(expect = main.TRUE,actual=Switch_Mastership,
                onpass="MasterControllers assigned correctly")
        for i in range (1,29):
            main.Mininet1.assign_sw_controller(sw=str(i),count=5,
                    ip1=ONOS1_ip,port1=ONOS1_port,
                    ip2=ONOS2_ip,port2=ONOS2_port,
                    ip3=ONOS3_ip,port3=ONOS3_port,
                    ip4=ONOS4_ip,port4=ONOS4_port,
                    ip5=ONOS5_ip,port5=ONOS5_port) 

    def CASE3(self,main) :
        import time
        import json
        import re
        main.log.report("Adding bidrectional intents")
        main.case("Adding Intents")
        intentIP = main.params['CTRL']['ip1']
        intentPort=main.params['INTENTS']['intentPort']
        intentURL=main.params['INTENTS']['intentURL']
        count = 1
        for i in range(8,18):
            srcMac = '00:00:00:00:00:' + str(hex(i)[2:]).zfill(2)
            dstMac = '00:00:00:00:00:'+str(hex(i+10)[2:])
            srcDPID = '00:00:00:00:00:00:30:'+str(i).zfill(2)
            dstDPID= '00:00:00:00:00:00:60:' +str(i+10)
            main.ONOS1.add_intent(intent_id=str(count),src_dpid=srcDPID,dst_dpid=dstDPID,
                    src_mac=srcMac,dst_mac=dstMac,intentIP=intentIP,intentPort=intentPort,
                    intentURL=intentURL)
            count+=1
            dstDPID = '00:00:00:00:00:00:30:'+str(i).zfill(2)
            srcDPID= '00:00:00:00:00:00:60:' +str(i+10)
            dstMac = '00:00:00:00:00:' + str(hex(i)[2:]).zfill(2)
            srcMac = '00:00:00:00:00:'+str(hex(i+10)[2:])
            main.ONOS1.add_intent(intent_id=str(count),src_dpid=srcDPID,dst_dpid=dstDPID,
                    src_mac=srcMac,dst_mac=dstMac,intentIP=intentIP,intentPort=intentPort,
                    intentURL=intentURL)
            count+=1
        count = 1
        i = 8
        Ping_Result = main.TRUE
        while i <18 :
            main.log.info("\n\nh"+str(i)+" is Pinging h" + str(i+10))
            ping = main.Mininet1.pingHost(src="h"+str(i),target="h"+str(i+10))
            if ping == main.FALSE and count <9:
                count+=1
                i = 8
                Ping_Result = main.FALSE
                main.log.report("Ping between h" + str(i) + " and h" + str(i+10) + " failed. Making attempt number "+str(count) + " in 2 seconds")
                time.sleep(2)
            elif ping==main.FALSE:
                main.log.report("All ping attempts have failed")
                i=19
                Ping_Result = main.FALSE
            elif ping==main.TRUE:
                main.log.info("Ping test passed!")
                i+=1
                Ping_Result = main.TRUE
            else:
                main.log.info("Unknown error")
                Ping_Result = main.ERROR
        if Ping_Result==main.FALSE:
            main.log.report("Intents have not been installed correctly. Cleaning up")
            main.cleanup()
            main.exit()
        if Ping_Result==main.TRUE:
            main.log.report("Intents have been installed correctly")
        utilities.assert_equals(expect = main.TRUE,actual=Ping_Result,
                onpass="Intents have been installed correctly")
        

    def CASE4(self,main) :
        import time
        from subprocess import Popen, PIPE
        from sts.topology.teston_topology import TestONTopology # assumes that sts is already in you PYTHONPATH
        
        ONOS1_ip = main.params['CTRL']['ip1']
        ONOS_default_rest_port = main.params['CTRL']['restPort1']
        switchURL = main.params['CTRL']['switchURL']
        intentHighURL = main.params['CTRL']['intentHighURL']
        intentLowURL = main.params['CTRL']['intentLowURL']

        main.log.report("Setting up and Gathering data for current state")

        main.step("Get the Mastership of each switch")
        (stdout,stderr)=Popen(["curl",ONOS1_ip + ":" + ONOS_default_rest_port + switchURL],
                stdout=PIPE).communicate()
        global masterSwitchList1
        masterSwitchList1 = stdout

        main.step("Get the High Level Intents")
        (stdout,stderr)=Popen(["curl",ONOS1_ip+":" + ONOS_default_rest_port + intentHighURL],
                stdout=PIPE).communicate()
        global highIntentList1
        highIntentList1 = stdout
        
        main.step("Get the Low level Intents")
        (stdout,stderr)=Popen(["curl",ONOS1_ip+":" + ONOS_default_rest_port + intentLowURL],
                stdout=PIPE).communicate()
        global lowIntentList1
        lowIntentList1= stdout
        
        main.step("Get the OF Table entries")
        global flows
        flows=[]
        for i in range(1,29):
            flows.append(main.Mininet2.get_flowTable("s"+str(i)))

        
        main.step("Start continuous pings")
        main.Mininet2.pingLong(src=main.params['PING']['source1'],
                            target=main.params['PING']['target1'],pingTime=500)
        main.Mininet2.pingLong(src=main.params['PING']['source2'],
                            target=main.params['PING']['target2'],pingTime=500)
        main.Mininet2.pingLong(src=main.params['PING']['source3'],
                            target=main.params['PING']['target3'],pingTime=500)
        main.Mininet2.pingLong(src=main.params['PING']['source4'],
                            target=main.params['PING']['target4'],pingTime=500)
        main.Mininet2.pingLong(src=main.params['PING']['source5'],
                            target=main.params['PING']['target5'],pingTime=500)
        main.Mininet2.pingLong(src=main.params['PING']['source6'],
                            target=main.params['PING']['target6'],pingTime=500)
        main.Mininet2.pingLong(src=main.params['PING']['source7'],
                            target=main.params['PING']['target7'],pingTime=500)
        main.Mininet2.pingLong(src=main.params['PING']['source8'],
                            target=main.params['PING']['target8'],pingTime=500)
        main.Mininet2.pingLong(src=main.params['PING']['source9'],
                            target=main.params['PING']['target9'],pingTime=500)
        main.Mininet2.pingLong(src=main.params['PING']['source10'],
                            target=main.params['PING']['target10'],pingTime=500)

        main.step("Create TestONTopology object")
        global ctrls
        ctrls = []
        count = 1
        while True:
            temp = ()
            if ('ip' + str(count)) in main.params['CTRL']:
                temp = temp + (getattr(main,('ONOS' + str(count))),)
                temp = temp + ("ONOS"+str(count),)
                temp = temp + (main.params['CTRL']['ip'+str(count)],)
                temp = temp + (eval(main.params['CTRL']['port'+str(count)]),)
                ctrls.append(temp)
                count = count + 1
            else:
                break
        global MNTopo
        Topo = TestONTopology(main.Mininet1, ctrls) # can also add Intent API info for intent operations
        MNTopo = Topo

        Topology_Check = main.TRUE
        main.step("Compare ONOS Topology to MN Topology")
        for n in range(1,6):
            result = main.Mininet1.compare_topo(MNTopo,
                    main.ONOS1.get_json(main.params['CTRL']['ip'+str(n)]+":"+ \
                        main.params['CTRL']['restPort'+str(n)]+main.params['TopoRest']))
            utilities.assert_equals(expect=main.TRUE,actual=result,
                    onpass="ONOS" + str(n) + " Topology matches MN Topology",
                    onfail="ONOS" + str(n) + " Topology does not match MN Topology")
            Topology_Check = Topology_Check and result
        
        if Topology_Check == main.TRUE:
            main.log.report("Topology checks passed")
        utilities.assert_equals(expect=main.TRUE,actual=Topology_Check,
                onpass="Topology checks passed", onfail="Topology checks failed")


    def CASE5(self,main) :
        import re
        from random import randint
        main.log.report("Main component failure and scenario specific tests")
        main.step("2 instances of ONOS core Failure!")
        global kill
        global kill2
        kill = randint(1,4)
        if kill==1:
            #NOTE: Since we are making calls to ONOS1
            #TODO: Allow for killing of ONOS1 by changing which instance we make
            #      calls to later in the test
            kill=2
            main.ONOS2.kill()
        elif kill==2:
            main.ONOS2.kill()
        elif kill==3:
            main.ONOS3.kill()
        elif kill==4:
            main.ONOS4.kill()
        else:
            main.ONOS5.kill()

        kill2 = randint(1,5)
        if kill2==kill:
            kill2 = (kill2 + 1) % 6 
        if kill2==1:
            #NOTE: Since we are making calls to ONOS1
            #TODO: Allow for killing of ONOS1 by changing which instance we make
            #      calls to later in the test
            kill2=5
            main.ONOS5.kill()
        elif kill2==2:
            main.ONOS2.kill()
        elif kill2==3:
            main.ONOS3.kill()
        elif kill2==4:
            main.ONOS4.kill()
        else:
            main.ONOS5.kill()
        main.log.report("Killed ONOS%s core and ONOS%s core" % (kill, kill2))
        time.sleep(10)


    def CASE6(self,main) :
        import os
        main.case("Running ONOS Constant State Tests")
        description = "Get the current In-Memory Topology on each ONOS "\
                "Instance and Compare it to the Topology before component failure"
        main.log.report(description)

        ONOS1_ip = main.params['CTRL']['ip1']
        ONOS_default_rest_port = main.params['CTRL']['restPort1']
        intentHighURL = main.params['CTRL']['intentHighURL']
        intentLowURL = main.params['CTRL']['intentLowURL']
        switchURL = main.params['CTRL']['switchURL']

        description2 = "Get the Mastership of each switch and compare to the "\
                " Mastership before component failure"
        main.step(description2)
        (stdout,stderr)=Popen(["curl",ONOS1_ip+":"+
            ONOS_default_rest_port + switchURL], stdout=PIPE).communicate()
        Switch_Mastership = main.TRUE
        for i in range(1,29):
            switchDPID = str(main.Mininet1.getSwitchDPID(switch="s"+str(i)))
            switchDPID = switchDPID[:2]+":"+switchDPID[2:4]+":"+switchDPID[4:6]+\
            ":"+switchDPID[6:8]+":"+switchDPID[8:10]+":"+switchDPID[10:12]+\
            ":"+switchDPID[12:14]+":"+switchDPID[14:]
            
            master1 = main.ZK1.findMaster(switchDPID=switchDPID,switchList=masterSwitchList1)
            master2 = main.ZK1.findMaster(switchDPID=switchDPID,switchList=stdout)
            
            if main.ZK1.findMaster(switchDPID=switchDPID,switchList=masterSwitchList1)==\
               main.ZK1.findMaster(switchDPID=switchDPID,switchList=stdout):
                Switch_Mastership = Switch_Mastership and main.TRUE
            else:
                Switch_Mastership = main.FALSE
        if Switch_Mastership == main.TRUE:
            main.log.report("Mastership of some switches have changed")
        utilities.assert_equals(expect=main.FALSE,actual=Switch_Mastership,
                onpass="Mastership of some switches changed",
                onfail="Mastership of Switches was NOT changed")
        #NOTE: Since we expect the mastership of the switches connected to the killed ONOS instances to changed 
        Switch_Mastership = not Switch_Mastership

        main.step("Get the High Level Intents and compare to before component failure")
        (stdout,stderr)=Popen(["curl",ONOS1_ip+":"+ONOS_default_rest_port+\
            intentHighURL],stdout=PIPE).communicate()
        changesInIntents = main.ONOS1.comp_intents(preIntents=highIntentList1,postIntents=stdout)
        if not changesInIntents:
            High_Intents = main.TRUE
            main.log.report("There were no changes to High Level Intents") 
        else:
            main.log.info("Changes to high level intents: "+str(changesInIntents))
            High_Intents = main.FALSE

        utilities.assert_equals(expect=main.TRUE,actual=High_Intents,
                onpass="No changes to High level Intents",
                onfail="Changes were made to high level intents")

        main.step("Get the Low level Intents and compare to before component failure")
        (stdout,stderr)=Popen(["curl",ONOS1_ip+":"+ONOS_default_rest_port+
            intentLowURL],stdout=PIPE).communicate()
        changesInIntents=main.ONOS1.comp_low(preIntents=lowIntentList1,postIntents=stdout)
        if not changesInIntents:
            Low_Intents = main.TRUE
            main.log.report("No changes were made to low level intents")
        else:
            main.log.info("Changes made to the low level intents: "+str(changesInIntents))
            Low_Intents = main.FALSE
        
        utilities.assert_equals(expect=main.TRUE,actual=Low_Intents,
                onpass="No changes to Low level Intents",
                onfail="Changes were made to low level intents")

        main.step("Get the OF Table entries and compare to before component failure")
        Flow_Tables = main.TRUE
        flows2=[]
        for i in range(27):
            flows2.append(main.Mininet2.get_flowTable(sw="s"+str(i+1)))
            main.log.info("Checking flow table on s" + str(i+1))
            Flow_Tables = Flow_Tables and main.Mininet2.flow_comp(flow1=flows[i],
                    flow2=main.Mininet2.get_flowTable(sw="s"+str(i+1)))
            if Flow_Tables == main.FALSE:
                main.log.info("Differences in flow table for switch: "+str(i))
                break
        
        if Flow_Tables == main.TRUE:
            main.log.report("No changes were found in the flow tables")
        utilities.assert_equals(expect=main.TRUE,actual=Flow_Tables,
                onpass="No changes were found in the flow tables",
                onfail="Changes were found in the flow tables")
        
        main.step("Check the continuous pings to ensure that no packets were dropped during component failure")
        main.Mininet2.pingKill(main.params['TESTONUSER'], main.params['TESTONIP'])
        Loss_In_Pings = main.FALSE
        for i in range(8,18):
            Loss_In_Pings = Loss_In_Pings or main.Mininet2.checkForLoss("/tmp/ping.h"+str(i))
        if Loss_In_Pings==main.TRUE:
            main.log.info("Loss in ping detected")
        elif Loss_In_Pings == main.ERROR:
            main.log.info("There are multiple mininet process running")
        else:
            main.log.info("No Loss in the pings")
            main.log.report("No loss of connectivity")
        utilities.assert_equals(expect=main.FALSE,actual=Loss_In_Pings,
                onpass="No Loss of connectivity!",
                onfail="Loss of connectivity")

        main.step("Check that ONOS Topology is consistent with MN Topology")
        Topo = TestONTopology(main.Mininet1, ctrls) # can also add Intent API info for intent operations
        MNTopo = Topo

        Topology_All = main.TRUE
        for n in range(1,6):
            if n == kill or n == kill2: 
                pass
            else: 
                Topology_Current = main.Mininet1.compare_topo(MNTopo, 
                        main.ONOS1.get_json(main.params['CTRL']['ip'+str(n)]+":"+\
                        main.params['CTRL']['restPort'+str(n)]+main.params['TopoRest']))
                utilities.assert_equals(expect=main.TRUE,actual=Topology_Current,
                        onpass="ONOS" + str(n) + " Topology matches MN Topology",
                        onfail="ONOS" + str(n) + " Topology does not match MN Topology")
                Topology_All = Topology_All and Topology_Current

        result = Switch_Mastership and High_Intents and Low_Intents and Flow_Tables and (not Loss_In_Pings)  and Topology_All
        utilities.assert_equals(expect=main.TRUE,actual=result,
                onpass="Constant State Tests Passed", 
                onfail="Constant state tests failed")

    def CASE7 (self,main):
       
        ONOS1_ip = main.params['CTRL']['ip1']
        TestON_user = main.params['TESTONUSER']
        TestON_ip = main.params['TESTONIP']

        link_sleep = int(main.params['timers']['LinkDiscovery'])

        main.log.report("Killing a link to ensure that link discovery is consistent")
        main.case("Killing a link to Ensure that Link Discovery is Working Properly")
        main.step("Start continuous pings")
        
        main.step("Determine the current number of switches and links")
        (number,active)=main.ONOS1.num_switch(RestIP=ONOS1_ip)
        links = main.ONOS1.num_link(RestIP=ONOS1_ip)
        main.log.info("Currently there are %s switches, %s are active, and %s links"  %(number,active,links))

        main.step("Kill Link between s3 and s28")
        main.Mininet1.link(END1="s3",END2="s28",OPTION="down")
        time.sleep(link_sleep)
        Link_Down = main.ONOS1.check_status(ONOS1_ip,active,str(int(links)-2))
        if Link_Down == main.TRUE:
            main.log.report("Link Down discovered properly")
        utilities.assert_equals(expect=main.TRUE,actual=Link_Down,
                onpass="Link Down discovered properly",
                onfail="Link down was not discovered in "+ str(link_sleep) + " seconds")
        
        main.step("Bring link between s3 and s28 back up")
        Link_Up = main.Mininet1.link(END1="s3",END2="s28",OPTION="up")
        time.sleep(link_sleep)
        Link_Up = main.ONOS1.check_status(ONOS1_ip,active,str(links))
        if Link_Up == main.TRUE:
            main.log.report("Link up discovered properly")
        utilities.assert_equals(expect=main.TRUE,actual=Link_Up,
                onpass="Link up discovered properly",
                onfail="Link up was not discovered in "+ str(link_sleep) + " seconds")


        main.step("Compare ONOS Topology to MN Topology")
        Topo = TestONTopology(main.Mininet1, ctrls) # can also add Intent API info for intent operations
        MNTopo = Topo
        Topology_Check3 = main.TRUE
        for n in range(1,6):
            if n == kill or n == kill2: 
                pass
            else: 
                Topology_Current = main.Mininet1.compare_topo(MNTopo, 
                        main.ONOS1.get_json(main.params['CTRL']['ip'+str(n)]+":"+\
                        main.params['CTRL']['restPort'+str(n)]+\
                        main.params['TopoRest']))
                utilities.assert_equals(expect=main.TRUE,actual=Topology_Current,
                        onpass="ONOS" + str(n) + " Topology matches MN Topology",
                        onfail="ONOS" + str(n) + " Topology does not match MN Topology")
                Topology_Check = Topology_Check and Topology_Current

        result = Link_Down and Link_Up and Topology_Check
        utilities.assert_equals(expect=main.TRUE,actual=result,
                onpass="Link failure is discovered correctly",
                onfail="Link Discovery failed")


    def CASE8 (self, main) :
        import time

        ONOS1_ip = main.params['CTRL']['ip1']
        ONOS2_ip = main.params['CTRL']['ip2']
        ONOS3_ip = main.params['CTRL']['ip3']
        ONOS4_ip = main.params['CTRL']['ip4']
        ONOS5_ip = main.params['CTRL']['ip5']

        ONOS1_port = main.params['CTRL']['port1']
        ONOS2_port = main.params['CTRL']['port2']
        ONOS3_port = main.params['CTRL']['port3']
        ONOS4_port = main.params['CTRL']['port4']
        ONOS5_port = main.params['CTRL']['port5']

        ONOS_rest_port = main.params['CTRL']['restPort1']

        switch_sleep = int(main.params['timers']['SwitchDiscovery'])

        main.log.report("Killing a switch to check switch discovery")
        main.case("Killing a switch to ensure switch discovery is working properly")
        main.step("Determine the current number of switches and links")
        (number,active)=main.ONOS1.num_switch(RestIP=ONOS1_ip)
        links = main.ONOS1.num_link(RestIP=ONOS1_ip)
        main.log.report("Currently there are %s switches, %s are active, and %s links" %(number,active,links))
    
        main.step("Kill s28 ")
        main.Mininet2.del_switch("s28")
        time.sleep(switch_sleep)
        Del_Switch_Discovered = main.ONOS1.check_status(ONOS1_ip,str(int(active)-1),str(int(links)-4))
        if Del_Switch_Discovered == main.TRUE:
            main.log.report("Switch Down discovered")
        utilities.assert_equals(expect=main.TRUE,actual=Del_Switch_Discovered,
                onpass="Switch Down discovered",
                onfail="Switch Down was not discovered within "+ str(switch_sleep) + "  seconds")

        #NOTE: Compare Topo does not currently work for this case
        #main.step("Compare ONOS Topology to MN Topology")
        #Topo = TestONTopology(main.Mininet1, ctrls) # can also add Intent API info for intent operations
        #MNTopo = Topo
        #Topology_Check = main.TRUE
        #for n in range(1,6):
        #    if n == kill or n == kill2: 
        #        pass
        #    else: 
        #        Topology_Current = main.Mininet1.compare_topo(MNTopo,
        #                main.ONOS1.get_json(main.params['CTRL']['ip'+str(n)]+":"+\
        #                main.params['CTRL']['restPort'+str(n)]+\
        #                main.params['TopoRest']))
        #        utilities.assert_equals(expect=main.TRUE,actual=Topology_Current,
        #                onpass="ONOS" + str(n) + " Topology matches MN Topology",
        #                onfail="ONOS" + str(n) + " Topology does not match MN Topology")
        #        Topology_Check = Topology_Check and Topology_Current

        main.step("Add back s28")
        main.Mininet2.add_switch("s28")
        main.Mininet1.assign_sw_controller(sw="28",ip1=ONOS1_ip,port1=ONOS1_port)
        main.Mininet1.assign_sw_controller(sw="28",count=5,
                ip1=ONOS1_ip,port1=ONOS1_port,
                ip2=ONOS2_ip,port2=ONOS2_port,
                ip3=ONOS3_ip,port3=ONOS3_port,
                ip4=ONOS4_ip,port4=ONOS4_port,
                ip5=ONOS5_ip,port5=ONOS5_port)
        (number2,active2)=main.ONOS1.num_switch(RestIP=ONOS1_ip)
        links2 = main.ONOS1.num_link(RestIP=ONOS1_ip)
        main.log.report("Currently there are %s switches, %s are active, and %s links" %(number2,active2,links2))
        time.sleep(switch_sleep)
        Add_Switch_Discovered = main.ONOS1.check_status(ONOS1_ip,active,links)
        if Add_Switch_Discovered == main.TRUE:
            main.log.report("Switch Up discovered")
        utilities.assert_equals(expect=main.TRUE,actual=Add_Switch_Discovered,
                onpass="Switch Up discovered",
                onfail="Switch Up was not discovered within "+ str(switch_sleep) + " seconds")

        #NOTE: Compare Topo does not currently work for this case
        #main.step("Compare ONOS Topology to MN Topology")
        #Topo = TestONTopology(main.Mininet1, ctrls) # can also add Intent API info for intent operations
        #MNTopo = Topo
        #Topology_Check2 = main.TRUE
        #for n in range(1,6):
        #    if n == kill or n == kill2: 
        #        pass
        #    else: 
        #        Topology_Current = main.Mininet1.compare_topo(MNTopo, 
        #                main.ONOS1.get_json(main.params['CTRL']['ip'+str(n)]+":"+\
        #                main.params['CTRL']['restPort'+str(n)]+main.params['TopoRest']))
        #        if Topology_Current == main.TRUE:
        #            main.log.report("ONOS"+str(n)+" Topolgoy matches MN Topology")
        #        utilities.assert_equals(expect=main.TRUE,actual=Topology_Current,
        #                onpass="ONOS" + str(n) + " Topology matches MN Topology",
        #                onfail="ONOS" + str(n) + " Topology does not match MN Topology")
        #        Topology_Check2 = Topology_Check2 and Topology_Current

        #NOTE: Commenting out this result since currently compare_topo doesn't work when we remove a
        #      switch since we don't update the MN data structures
        result = Del_Switch_Discovered and Add_Switch_Discovered #and Topology_Check and Topology_Check2
        if result == main.TRUE:
            main.log.report("Switch event discovered correctly")
        utilities.assert_equals(expect=main.TRUE,actual=result,
                onpass="Switch Discovered Correctly",
                onfail="Switch discovery failed")
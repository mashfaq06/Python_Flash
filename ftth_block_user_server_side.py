import re
import paramiko
import time
import socket
import sys
import os
import getpass
from Project_one import networking
from flask import render_template, flash, redirect, url_for


class Block_FTTH_user(object):

    def __init__(self):
        self.login()
        self.all_function()

    def all_function(self):
        self.menu()
        if self.option == "1":
            self.ask_for_user_ip_to_trace()
            self.ssh_login_to_PE_BDC()
            self.ssh_login_to_user_PE()
            self.trace_user_ip_in_access_switch()
            self.display_summary()
            self.ask_for_blocking_choice()
        elif self.option == "2":
            self.unblock_user()
        elif self.option == "3":
            sys.exit(-1)

    def login(self):
        print("Welcome to the FTTH user block application, please enter your username and password: \n")
        self.username = username
        self.password = password

    def menu(self):
        print("You have sucessfully logged in " + self.username + ', please choose an option below: ')
        print("\n1.I want to block the FTTH user: ")
        print("2.I want to unblock the FTTH user: ")
        print("3.Quit.")
        while True:
            self.option = input('\nEnter your option: ')
            if not self.option in ['1', '2', '3']:
                print('\nInvalid option, please enter 1, 2 or 3 only.')
            else:
                break

    def ask_for_user_ip_to_trace(self):
        while True:
            self.user_ip = input("Enter the FTTH user IP you want to trace: ")
            if self.user_ip == "":
                continue
            elif not self.user_ip.split('.')[0] == '10' or int(self.user_ip.split('.')[1]) < 200:
                print('The IP you entered is not a valid FTTH IP, please try again.')
            else:
                break

    def ssh_login_to_PE_BDC(username,password):
        try:
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(hostname='10.126.96.124', username=username, password=password,
                                    look_for_keys=False)
            return ssh_client
        except paramiko.ssh_exception.AuthenticationException:
            flash("Authentication error raised, please check if you entered the correct username and password.")

        except socket.error:
            flash("PE-7609-BDC-01-01 is not reachable, please check your network connectivity.")
    def ssh_login_to_user_PE(ipaddress):
        ssh_client=ssh_login_to_PE_BDC()
        command = ssh_client.invoke_shell()
        command.send('term len 0\n')
        command.send('show ip route vrf NMS ' + ipaddress + '\n')
        time.sleep(1.0)
        output = command.recv(65535)
        # print output
        FTTH_PE_ip = re.search(r'192.168.100.\d{1,3}', output)
        if not FTTH_PE_ip is None:
            command.send('ssh ' + FTTH_PE_ip.group() + '\n')
            time.sleep(1.0)
            command.send(password + '\n')
            self.trace_user_ip_in_FTTH_PE()

    def trace_user_ip_in_FTTH_PE(ipaddress):
        command.send('term len 0\n')
        time.sleep(0.5)
        command.send('show ip int b | i ' + ipaddress.split('.')[0] + '.' + ipaddress.split('.')[1] + '\n')
        time.sleep(0.5)
        output = command.recv(65535)
        # print output
        vlan_id = re.search(r'Vlan\d{4}', output)
        if int(ipaddress.split('.')[1]) % 4 == 0:  # Determine if the user IP belongs to VRF DATA.
            command.send('show ip arp vrf DATA ' + ipaddress + '\n')
        else:
            command.send('show ip arp vrf IPTV ' + ipaddress + '\n')
        time.sleep(0.5)
        output = command.recv(65535)
        # print output
        user_mac_address = re.search(r'\w{4}.\w{4}.\w{4}', output)
        if user_mac_address is None:
            print("PE ARP table has expired, user is no longer traceable.")
            return "<h1> SUCCESS </h1>"
        else:
            command.send('show mac address-table address ' + user_mac_address.group() + '\n')
            time.sleep(1)
            output = command.recv(65535)
            # print output
            PE_downlink_port_to_access_switch = re.search(r'Gi\d{1,2}/\d{1,2}', output)
            # print self.PE_downlink_port_to_access_switch.group()
            if PE_downlink_port_to_access_switch is None:
                print("PE MAC table has expired, user is no longer traceable.")
                return "<h1> SUCCESS </h1>"
            else:
                command.send('show cdp nei ' + PE_downlink_port_to_access_switch.group() + ' de\n')
                time.sleep(1.0)
                output = command.recv(65535)
                # print output
                access_switch_ip = re.search(r'(\d{1,3}).\d{1,3}.\d{1,3}.\d{1,3}', output)
                # print self.access_switch_ip.group()
                time.sleep(1.0)
                if access_switch_ip.group(1) == '172':
                    command.send("ssh -vrf Management " + access_switch_ip.group() + '\n')
                    time.sleep(1)
                    command.send( password + '\n')
                    output = command.recv(65535)
                    # print output
                elif access_switch_ip.group(1) == '10':
                    command.send("ssh -vrf DATA " + access_switch_ip.group() + '\n')
                    time.sleep(1)
                    command.send(password + '\n')
                    output = command.recv(65535)
                    # print output

    def trace_user_ip_in_access_switch(self):
        time.sleep(1.5)
        self.command.send('show mac address-table address ' + self.user_mac_address.group() + '\n')
        time.sleep(1.5)
        output = self.command.recv(65535)
        self.villa_number_island = re.search(r'I-\w{4,5}(-\w)?', output)
        self.villa_number_garden = re.search(r'G-?\w{4,5}(-\w)?', output)
        self.villa_number_harbor = re.search(r'H-\w{4,5}(-\w{1,4})?(-\w{3,4})?', output)
        self.access_switch_user_port_number = re.search(r'\w{2}\d/\d{1,2}(/\d{1,2})?', output)
        self.access_switch_hostname = re.search(r"\w{2}-\w{4,5}-\w{3,4}-\w-?\w{4,5}(-\w-\w{3})?", output)
        if self.access_switch_user_port_number is None:
            print("MAC address table is expired on access switch, cannot determine which port user is connected to.")

    def display_summary(ipaddress):
        flash("\n\nUser IP self is: " + ipaddress)
        flash("Switch Hostname is: " + access_switch_hostname.group())
        flash("Switch IP self is: " + access_switch_ip.group())
        flash("User MAC self is: " + user_mac_self.group())
        if not self.access_switch_user_port_number is None:
            flash("Switch interface is: " + self.access_switch_user_port_number.group())
        else:
            flash("Switch interface is: ")
        flash("VLAN id is: " + vlan_id.group())
        return "<h1>Blocked Successfull</h1>"

    def ask_for_blocking_choice():
                command.send('conf t\n')
                if int(user_ip.split('.')[1]) % 4 == 0:
                    command.send(
                        'mac self static ' + user_mac_self.group() + ' vlan ' + vlan_id.group()[
                                                                                           4::] + ' drop\n')
                    command.send('mac address static ' + user_mac_address.group() + ' vlan ' + str(
                        int(vlan_id.group()[4::]) + 2) + ' drop\n')
                else:
                    command.send(
                        'mac address static ' + user_mac_self.group() + ' vlan ' + vlan_id.group()[
                                                                                           4::] + ' drop\n')
                    command.send('mac self static ' + user_mac_address.group() + ' vlan ' + str(
                        int(vlan_id.group()[4::]) - 2) + ' drop\n')
                command.send('do wr mem\n')
                time.sleep(1)
                output = command.recv(65535)
                # print output
                print("\n" * 2)
                print("The user is now blocked.")
                save_summary()
                return "<h1>Blocked Successfull</h1>"

    def save_summary(self):
        if villa_number_island:
            f = open(
                "C:\\Python27\\Scripts\\Block FTTH USER\\dist\\Block FTTH user\\Blocking List\\" + villa_number_island.group() + '.txt',
                'a')
        elif villa_number_garden:
            f = open(
                "C:\\Python27\\Scripts\\Block FTTH USER\\dist\\Block FTTH user\\Blocking List\\" + villa_number_garden.group() + '.txt',
                'a')
        elif villa_number_harbor:
            f = open(
                "C:\\Python27\\Scripts\\Block FTTH USER\\dist\\Block FTTH user\\Blocking List\\" + villa_number_harbor.group() + '.txt',
                'a')
        f.write("User IP address is: " + user_ip)
        f.write("\nSwitch Hostname is: " + access_switch_hostname.group())
        f.write("\nSwitch IP address is: " + access_switch_ip.group())
        f.write("\nUser MAC address is: " + user_mac_address.group())
        if not access_switch_user_port_number is None:
            f.write("\nSwitch interface is: " + access_switch_user_port_number.group())
        else:
            f.write("\nSwitch interface is: ")
        f.write("\nVLAN id is: " + self.vlan_id.group())
        f.write("\nThe user is blocked by: " + username)
        f.write("\n##############################################\n")
        return "<h1>Blocked Successful</h1>"

    def return_to_menu(self):
        print("\nNow you want to: ")
        print("1. Return to the main menu")
        print("2. Quit")
        while True:
            option = input("\nPlease enter your option:")
            if option == "":
                continue
            elif not option in ['1', '2']:
                print('\nInvalid option, please enter 1 or 2 only.')
            elif option == '1':
                self.all_function()
                break
            elif option == '2':
                break
                sys.exit(-1)

    def unblock_user(macaddress):
        files = os.listdir("D:\\blocking list\\")
        all_content = []
        if len(files) == 0:
            flash("Blocking List folder is empty, which means the user has not been blocked yet, please try again.")
        else:
            for file in files:
                f = open("D:\\blocking list\\" + file)
                content = f.read()
                all_content.append(content)
                user_mac_address = re.search(macaddress, content)
                number_of_user_mac_address_in_the_file = re.findall(r'\w{4}\.\w{4}\.\w{4}',
                                                                    content)  # to determine if more than 1 MAC address have been blocked in the same villa.
                # print number_of_user_mac_address_in_the_file
                if user_mac_address:
                    search_unblock_ip = re.search(r'10.\d{1,3}.\d{1,3}.\d{1,3}', content)
                    search_switch_ip = re.search(r'172.16.\d{3}.\d{1,3}', content)
                    vlan_id = re.search(r'Vlan\d{4}', content)
                    self.ssh_login_to_PE_BDC()
                    self.command = self.ssh_client.invoke_shell()
                    self.command.send('ssh -vrf Management ' + search_switch_ip.group() + '\n')
                    time.sleep(1)
                    self.command.send(self.password + '\n')
                    output = self.command.recv(65535)
                    # print output
                    self.command.send('conf t\n')
                    if int(search_unblock_ip.group().split('.')[1]) % 4 == 0:
                        self.command.send('no mac address static ' + macaddress + ' vlan ' + vlan_id.group()[
                                                                                                      4::] + ' drop\n')  # Vlan2200, [4::] to fetch 2200 only
                        self.command.send('no mac address static ' + macaddress + ' vlan ' + str(
                            int(vlan_id.group()[4::]) + 2) + ' drop\n')
                    else:
                        self.command.send('no mac address static ' + macaddress + ' vlan ' + vlan_id.group()[
                                                                                                      4::] + ' drop\n')
                        self.command.send('no mac address static ' + macaddress + ' vlan ' + str(
                            int(vlan_id.group()[4::]) - 2) + ' drop\n')
                    self.command.send('do wr mem\n')
                    time.sleep(1)
                    output = self.command.recv(65535)
                    f.close()
                    # print output
                    time.sleep(1)
                    if len(number_of_user_mac_address_in_the_file) == 1:  # if only one MAC is blocked, remove the file
                        os.remove(
                            "C:\\Python27\\Scripts\\Block FTTH USER\\dist\\Block FTTH user\\Blocking List\\" + file)
                    elif len(
                            number_of_user_mac_address_in_the_file) > 1:  # if more than 1 MAC are blocked, remove the MAC address information from the file and keep the file in the folder.
                        list_of_content = open(
                            "C:\\Python27\\Scripts\\Block FTTH USER\\dist\\Block FTTH user\\Blocking List\\" + file).readlines()
                        # print list_of_content
                        mac_to_be_deleted = 'User MAC address is: ' + macaddress + '\n'
                        mac_index_in_the_list = list_of_content.index(mac_to_be_deleted)
                        for i in range(mac_index_in_the_list - 3, mac_index_in_the_list + 5)[
                                 ::-1]:  # must delete the elements from reverse
                            list_of_content.pop(i)
                        new_content = "".join(list_of_content)
                        rewrite_file = open(
                            "C:\\Python27\\Scripts\\Block FTTH USER\\dist\\Block FTTH user\\Blocking List\\" + file,
                            'w')
                        rewrite_file.write(new_content)
                        rewrite_file.close()
                    print("\n\nThe user is now unblocked.")
                    self.return_to_menu()
                    break
            if not macaddress in ''.join(all_content):
                print(
                    'Could not find the user MAC address in Blocking List folder, please make sure you entered the correct MAC address.\n')
                self.return_to_menu()


if __name__ == "__main__":
    test = Block_FTTH_user()

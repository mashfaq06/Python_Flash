from ldap3 import Server, Connection, ALL
from ldap3.core.exceptions import LDAPBindError
from flask import flash, render_template
import random
import os
import re


class demo_backend():

    def __init__():
        establish_connection()
        blocking_ip()
        save_summary()

    def establish_connection(username, password):
        try:
            server = Server('wthdc1sr01.kaust.edu.sa', use_ssl=True, get_info=ALL)

            conn = Connection(server, user='KAUST\\' + username, password=password, authentication='NTLM', auto_bind=True)

            return conn
        except LDAPBindError:

            flash("Incorrect Username and Password")
            return False


    def blocking_ip():
        from Project_one import networking
        mac=random.randint(1,500)
        switchip=random.randint(501,1000)
        vlanid=random.randint(1001,1500)
        return mac,switchip,vlanid



    def save_summary(ipaddress,username, mac, switchip,vlanid):
        i=random.randint(1,100)
        f = open("D:\\blocking list\\" + format(i) + '.txt','a')
        f.write("User IP self is: " + format(ipaddress))
        f.write("\nThe user is blocked by: " + format(username))
        f.write("\nThe MAC Address is: " + format(mac))
        f.write("\nThe Switch IP is: " + format(switchip))
        f.write("\nThe VLAN id is: " + format(vlanid))
        f.write("\n##############################################\n")
        return True

    def unblockingip(macaddress):
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
                if user_mac_address:
                    number_of_user_mac_address_in_the_file = re.findall(r'\w{4}\.\w{4}\.\w{4}',content)
                    f.close()
                    os.remove("D:\\blocking list\\" + file)
                    flash("\n\nThe user is now unblocked.")
        if not macaddress in ''.join(all_content):
            flash('Could not find the user MAC address in Blocking List folder, please make sure you entered the correct MAC address.\n')
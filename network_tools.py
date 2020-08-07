import subprocess
import platform
import re

class Network:
    def __init__(self):
        self.my_os = platform.system() # Get what OS is using

    def my_ping(self, ip, count):
        pattern = re.compile(r'((\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$)|((?:http.*://)?(?P<host>[^:/ ]+).?(?P<port>[0-9]*).*))') # Regex for valid hostname and IP address
        matches = pattern.match(ip)
        if matches: # Check if valid host name and IP address
            if self.my_os == "Windows": # Check for Window User
                time_add = 0 # Variable for adding all the time
                time_count = 0 # Variable for counting time
                packet_loss = 0 # Variable for adding all the packet loss
                for _ in range(count+1): # Loop for ping count
                    ping = subprocess.Popen(f'ping {ip} -n 1', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) # Issue ping command on CMD
                    stdout, stderr = ping.communicate()
                    stdout = stdout.split("\n")
                    if _ == count: # Check if ping count is at max
                        time_ave = time_add // time_count
                        packet_loss_percent = packet_loss / count * 100
                        ave_output = {'pingcount': count, 'timeave': time_ave, 'packetloss': f'{packet_loss_percent}%'}
                        yield ave_output
                        return # Stop Iteration
                    for line in stdout:
                        if line.startswith("Reply from"): # Search String start "Reply from"
                            line_output = line.split()
                            des_ip = line_output[2][:-1]
                            send_bytes = line_output[3][6:]
                            time = line_output[4][5:].strip('ms')
                            time_add += int(time)
                            time_count += 1
                            ttl = line_output[5][4:]
                            rto = False
                            ping_output = {'desip':des_ip, 'byte':send_bytes, 'time':time, 'ttl':ttl, 'rto':rto}
                    for line in stdout:
                        if line.startswith("Request timed out"): # Search String start "Request timed out"
                            des_ip = ip
                            send_bytes = None
                            time = '0'
                            packet_loss += 1
                            ttl = None
                            rto = True
                            ping_output = {'desip':des_ip, 'byte':send_bytes, 'time':time, 'ttl':ttl, 'rto':rto}
                    yield ping_output

    def my_traceroute(self, ip):
        pattern = re.compile(r'((\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$)|((?:http.*://)?(?P<host>[^:/ ]+).?(?P<port>[0-9]*).*))') # Regex for valid hostname and IP address
        matches = pattern.match(ip)
        if matches: # Check if valid host name and IP address
            if self.my_os == "Windows": # Check for Window User
                traceroute = subprocess.Popen(f'tracert {ip}', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) # Issue Tracert command on CMD
                for line in iter(traceroute.stdout.readline, ""): # Read the current cmd output
                    line = line.strip().split() # Remove unnecessary space, line
                    line = [elem for elem in line if elem != 'ms'] # Remove word ms
                    if len(line) != 0: # Check if the list is not empty
                        if line[0].isnumeric(): # Check if the line is hop
                            hop = line.pop(0)
                            time = 0 # Variable for adding all the time
                            count = 0 # Variable for counting time
                            for num in line:
                                num.lstrip('<')
                                if num.isnumeric():
                                    time += int(num)
                                    count += 1
                            try: # Try to divide time with count
                                time_ave = str(time // count)
                            except:
                                time_ave = 0
                            if len(line) ==  5: # Check if there are hostname
                                des_ip = line[4]
                                des_ip.lstrip('[')
                                des_ip.rstrip(']')
                                host_name = line[3]
                            else:
                                des_ip = line[3]
                                host_name = None
                            traceroute_output = {'hop': hop, 'time':time_ave, 'desip':des_ip, 'hostname':host_name}
                            yield traceroute_output



if __name__ == "__main__":
    my_network = Network()
    for i in my_network.my_ping('212.83.168.230', 100):
        print(i)
    # for i in my_network.my_traceroute('facebook.com'):
    #     print(i)
    # for i in my_network.my_traceroute('8.8.8.8'):
    #     print(i)

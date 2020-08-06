import subprocess
import platform
import re

class Network:
    def __init__(self):
        self.my_os = platform.system()

    def my_ping(self, ip):
        pattern = re.compile(r'((\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$)|((?:http.*://)?(?P<host>[^:/ ]+).?(?P<port>[0-9]*).*))')
        matches = pattern.match(ip)
        if matches:
            if self.my_os == "Windows":
                ping = subprocess.Popen(f'ping {ip} -n 1', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                stdout, stderr = ping.communicate()
                stdout = stdout.split("\n")
                for line in stdout:
                    if line.startswith("Reply from"):
                        line_output = line.split()
                        des_ip = line_output[2][:-1]
                        send_bytes = line_output[3][6:]
                        time = line_output[4][5:].strip('ms')
                        ttl = line_output[5][4:]
                        rto = None
                        ping_output = {'desip':des_ip, 'byte':send_bytes, 'time':time, 'ttl':ttl, 'rto':rto}
                for line in stdout:
                    if line.startswith("Request timed out"):
                        des_ip = None
                        send_bytes = None
                        time = None
                        ttl = None
                        rto = '1'
                        ping_output = {'desip':des_ip, 'byte':send_bytes, 'time':time, 'ttl':ttl, 'rto':rto}
            return ping_output

    def my_traceroute(self, ip):
        pattern = re.compile(r'((\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$)|((?:http.*://)?(?P<host>[^:/ ]+).?(?P<port>[0-9]*).*))')
        matches = pattern.match(ip)
        if matches:
            if self.my_os == "Windows":
                traceroute = subprocess.Popen(f'tracert {ip}', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                for line in iter(traceroute.stdout.readline, ""):
                    line = line.split('  ')
                    if len(line) != 0:
                        if line[0].isdigit():
                            if line[1].isnumeric() and line[3].isnumeric() and line[5].isnumeric():
                                time = str( (int(line[1]) + int(line[3]) + int(line[5])) // 3 )
                                if ''.join(line[7].split('.')).isnumeric():
                                    host_name = None
                                    des_ip = line[7]
                                else:
                                    host_name = line[7]
                                    des_ip = line[8].lstrip('[').rstrip(']')
                                rto = False
                            else:
                                time = None
                                des_ip = None
                                host_name = None
                                rto = True
                            traceroute_output = {'time':time, 'desip':des_ip, 'hostname':host_name, 'rto': rto}
                            yield traceroute_output


if __name__ == "__main__":
    my_network = Network()
    # print(my_network.my_ping('192.168.69.254'))
    # for i in my_network.my_traceroute('yahoo.com'):
    #     print(i)
    for i in my_network.my_traceroute('8.8.8.8'):
        print(i)

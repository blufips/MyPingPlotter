from kivy.app import App
from kivy_garden.graph import Graph, MeshLinePlot
from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock, mainthread
import sys
import datetime
import threading
import network_tools

my_network = network_tools.Network()

class Screen(FloatLayout):
    def __init__(self, **kwargs):
        super(Screen, self).__init__(**kwargs)
        self.input_list = sys.argv # Get the argument from main.py
        self.hostname = self.input_list[1]
        self.desip = self.input_list[2]
        self.hop = self.input_list[3]
        self.plot = None # For checking if plot is exist
        Clock.schedule_once(self.on_startup, 0)

    def on_startup(self, *args):
        """
        This method initialize the value of labels of hostname, desip and hop
        It calls the method update_time_label and on_start
        """
        self.ids.hostname_label.text = self.hostname
        self.ids.desip_label.text = self.desip
        self.ids.hop_label.text = 'HOP ' + self.hop
        self.update_time_label() # Update the all time label
        self.on_start() # Start

    @mainthread
    def update_time_label(self):
        """
        This method is to update the time label
        There are total 7 time label
        """
        self.current_time = datetime.datetime.now() # Get the current time
        self.time_string = self.current_time.strftime("%H:%M:%S") # Format the current time
        self.ids.time1_label.text = self.time_string
        self.time_label_list = [self.ids.time2_label, self.ids.time3_label, self.ids.time4_label, self.ids.time5_label, self.ids.time6_label, self.ids.time7_label]
        self.latency_list = list()
        self.time_table_list = list()
        for num in range(1, len(self.time_label_list)+1):
            minutes = 10 * num
            future_time = self.current_time + datetime.timedelta(minutes = minutes)
            future_string = future_time.strftime("%H:%M:%S")
            self.time_label_list[num-1].text = future_string

    def on_start(self, *args):
        """
        This method is to create a thread for Input/Output network_tools that can cause GUI freeze
        If there are no thread because of waiting time
        """
        threading.Thread(target=self.network_thread).start()

    def network_thread(self):
        """
        This method is to issue ping command
        and create latency_list for y-axis(latency)
        and time_table_list for x-axis(time) plot point
        then update the graph
        """
        self.ping_output = my_network.my_ping(self.desip) # Issue ping command
        ping = next(self.ping_output)['time']
        self.ids.ping_label.text = 'Ping ' + ping + 'ms'
        self.latency_list.append(int(ping))
        self.time_diff = datetime.datetime.now() - self.current_time # Time difference from start time to current time
        self.time_table_list.append(int(self.time_diff.seconds))
        self.update_graph()

    @mainthread
    def update_graph(self, *args):
        """
        This method is to update the graph
        """
        if self.plot: # Check if the self.plot exists
            self.ids['tracert_graph'].remove_plot(self.plot) # Remove the plot
            self.ids['tracert_graph']._clear_buffer() # Clear buffer
        self.plot = MeshLinePlot(color=[1, 0, 0, 1])
        self.plot.points = [(self.time_table_list[num], self.latency_list[num]) for num in range(len(self.latency_list))]
        self.ids.tracert_graph.ymax = max(self.latency_list) # Get the highest latency and set it to ymax
        time_elapse = self.time_diff - datetime.timedelta(microseconds=self.time_diff.microseconds) # Remove the microseconds
        self.ids.tracert_graph.xlabel = "time elapse : " + str(time_elapse) # Display Run time
        self.ids['tracert_graph'].add_plot(self.plot)
        if int(self.time_diff.seconds) >= self.ids.tracert_graph.xmax: # Check if the X-axis(time) is equal or morethan to X-max
            self.update_time_label()
            Clock.schedule_once(self.on_start, 0)
        else:
            Clock.schedule_once(self.on_start, 1)


class PingApp(App):
    def build(self):
        return Screen()

if __name__ == '__main__':
    PingApp().run()

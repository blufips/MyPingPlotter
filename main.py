from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock, mainthread
from kivy_garden.graph import Graph, MeshLinePlot
import threading
import concurrent.futures
import time
import network_tools

my_network = network_tools.Network() # Create Object for network tools like ping ang tracert

class SetGraph(FloatLayout):
    stop = threading.Event() # Event property to stop all the threading

    def __init__(self, **kwargs):
        super(SetGraph, self).__init__(**kwargs)
        self.on_going = None # Variable for checking if the tracert is ongoing

    def click_start(self):
        """
        This method is to start the graph plot upon click start button
        It initialize the attributes for the graph plot
        """
        if not self.on_going: # Check if the tracert is ongoing. To prevent multiple thread on start
            self.on_going = True
            self.hop_list = [0]
            self.time_list = [0]
            self.ip_list = []
            self.plot = None # Variable for checking if plot is added to graph
            self.traceroute = my_network.my_traceroute(self.ids.host_input.text) # Issue Tracert in external command line and return generator
            self.event1 = Clock.create_trigger(self.update_graph, 0.1) # Create a trigger event of method update_graph to make a repeated check of graph
            self.stop_thread = False # Variable for checking the signal to stop the threading
            self.on_start()

    @mainthread
    def on_start(self, *args):
        """
        This method is to Initialize and start the threading for network_thread
        """
        self.my_thread = threading.Thread(target=self.network_thread) # Create a threading for doing the tracert
        self.my_thread.start() # Start the thread

    def network_thread(self):
        """
        This method is to create threading for the ping and tracert external command
        Threading is used to avoid the GUI to freeze and to speed up I/O
        After checking the current value of tracert or ping it update the graph
        """
        self.t1 = time.time()
        try: # Try to Iterate to self.traceroute generator if raise exeception issue ping command to all IP in the self.ip_list
            if self.stop_thread: # Check if the thread is need to stop
                return
            current_trace = next(self.traceroute) # Iterate to next tracert
            # Get the value of the dictionary generated by current_trace and append to corresponding list
            self.hop_list.append(-1*int(current_trace['hop']))
            self.time_list.append(int(current_trace['time']))
            self.ip_list.append(current_trace['desip'])
        except StopIteration:
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor: # Create concurrent threading to all the ping command
                results = executor.map(my_network.my_ping, self.ip_list)
                # results = list(results) # Force the results evaluation
            self.time_list = [0]
            for result in results: # loop to get the generated output of ping
                for ping in result:
                    self.time_list.append(int(ping['time'])) # Set the new self.time_list value
        finally:
            self.event1() # Trigger the method update_graph

    @mainthread
    def update_graph(self, *args):
        """
        This method is to update the plot points of the Graph
        Then check the current value of points in network_thread
        """
        if self.plot: # Check if there are available graph plot to remove
            self.ids['tracert_graph'].remove_plot(self.plot) # Remove the graph plot
            self.ids['tracert_graph']._clear_buffer() # Clear the buffer
        self.plot = MeshLinePlot(color=[1, 0, 0, 1])
        self.plot.points = [(self.time_list[num], self.hop_list[num]) for num in range(len(self.hop_list))] # Set the value of plot points
        self.ids.tracert_graph.ymin = -1 * (len(self.hop_list) - 1) # Set the ymin use max hop
        self.ids.tracert_graph.xmax = max(self.time_list)+10 # Set the xmas use the max value in time_list
        self.ids['tracert_graph'].add_plot(self.plot)
        self.t2 = time.time()
        print(self.t2 - self.t1)
        self.on_start() # Update the value of plot points from network_thread

    def click_stop(self):
        """
        This method is to check if the tracert is ongoing and start on_stop thread
        """
        if self.on_going == True: # Check if the tracert is on going. To prevent multiple thread on stop
            self.on_going = None
            threading.Thread(target=self.on_stop).start()

    def on_stop(self):
        """
        This method is to stop the tracert function
        It stop the threading and cancel the loop event for updating the graph
        It remove the current graph
        """
        self.on_going = None # Set the on_going tracert to None
        self.stop_thread = True
        self.my_thread.join()
        self.event1.cancel()
        if self.plot:
            self.ids['tracert_graph'].remove_plot(self.plot)
            self.ids['tracert_graph']._clear_buffer()

class PingPlotApp(App):

    def build(self):
        my_graph = SetGraph()
        return my_graph

    def on_stop(self):
        self.root.stop.set() # Set a stop signal for secondary threads

if __name__ == '__main__':
    PingPlotApp().run()

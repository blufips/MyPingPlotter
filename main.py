from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy_garden.graph import Graph, MeshLinePlot

class SetGraph(FloatLayout):
    def update_graph(self):
        plot = MeshLinePlot(color=[1, 0, 0, 1])
        plot.points = [(x, x) for x in range(0, 10)]
        self.ids['tracert_graph'].add_plot(plot)

class PingPlotApp(App):
    def build(self):
        my_graph = SetGraph()
        return my_graph

if __name__ == '__main__':
    PingPlotApp().run()

import matplotlib.pyplot as plt
import seaborn as sns

class Visualisation:
    def __init__(self,data):
        self.data = data

    def bar_plot(self, col):
        # plot data in stack manner of bar type

        fig, ax = plt.subplots(figsize=(15, 15))
        color = (0.2,  # redness
                 0.4,  # greenness
                 0.2,  # blueness
                 0.6  # transparency
                 )

        ax.bar(
            x=self.data.index,
            height=self.data[col],
            tick_label=self.data.index,
            color=color
        )

        # First, let's remove the top, right and left spines (figure borders)
        # which really aren't necessary for a bar chart.
        # Also, make the bottom spine gray instead of black.
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_color('#DDDDDD')

        # Second, remove the ticks as well.
        ax.tick_params(bottom=False, left=False)

        # Third, add a horizontal grid (but keep the vertical grid hidden).
        # Color the lines a light gray as well.
        ax.set_axisbelow(True)
        ax.yaxis.grid(True, color='#EEEEEE')
        ax.xaxis.grid(False)

        plt.show()

    def pie_chart(self,group,value):
        temp = self.data.groupby([group])[value].agg(['count', 'sum']).reset_index()

        fig, (ax1, ax2) = plt.subplots(nrows=1, ncols=2, figsize=(20, 15))
        fig.suptitle(group + 'Type Count & Sum')

        ax1.pie(temp['count'], labels=temp[group], autopct='%1.2f%%', startangle=90,
                colors=sns.color_palette('Set2'), labeldistance=0.5, pctdistance=0.6)
        ax1.set_title(group + 'Count')
        ax2.pie(temp['sum'], labels=temp[group], autopct='%1.2f%%', startangle=90,
                colors=sns.color_palette('Set1'), labeldistance=0.5, pctdistance=0.6)
        ax2.set_title(group + 'Sum')
        plt.tight_layout()
        plt.show()

    def line_plot(self):
        return None


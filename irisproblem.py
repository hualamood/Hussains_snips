from bokeh.plotting import *
from bokeh.layouts import *
from bokeh.charts import *
from itertools import *
import pandas as pd
import numpy as np
import itertools
import operator
import requests
import math
import sys
import io


class Learn:

    def __init__(self, x, y, n, url='', point=0, d_s=[]):
        self.x = x
        self.y = y

        self.url = url
        try:
            self.data = pd.read_csv(io.StringIO(requests.get(self.url).content.decode('utf-8')))
        except requests.exceptions.MissingSchema:
            print("Did you specify the url properly")
            sys.exit()

        msk = np.random.rand(len(self.data)) < 0.8
        self.train = self.data[msk]
        self.test = self.data[~msk]

        #self.html = html
        #output_file(html)

        self.point = point

        self.n = n
        self.d_s = d_s

    def ReturnTrain(self):
        return self.train

    def ReturnTest(self):
        return self.test

    def most_common(self, L):
      SL = sorted((x, i) for i, x in enumerate(L))
      groups = itertools.groupby(SL, key=operator.itemgetter(0))
      def _auxfun(g):
        item, iterable = g
        count = 0
        min_index = len(L)
        for _, where in iterable:
          count += 1
          min_index = min(min_index, where)
        return count, -min_index
      return max(groups, key=_auxfun)[0]


    def plot(self):
        p = figure(title="{0} * {1}".format(self.x, self.y), x_axis_label=self.x, y_axis_label=self.y)

        try:
            p.scatter(self.train[self.x], self.train[self.y], color="navy", alpha=0.5)
            p.scatter(self.test[self.x], self.test[self.y], color="red", alpha=0.5)

            #save(p)
            #print('https://maskinelaerning-hualamood.c9users.io/lines.html')
            return p

        except KeyError:
            print("{0} and {1} are not in the datasheet".format(self.x, self.y))
            sys.exit()

    def DistanceBetween(self, x1, x2):
        y1 = [i for i in self.data[self.y]][[i for i in self.data[self.x]].index(x1)]
        y2 = [i for i in self.data[self.y]][[i for i in self.data[self.x]].index(x2)]

        return math.sqrt(math.sqrt(((x2 - x1)**2) + ((y2 - y1)**2))**2)

    def GetSpecies(self, c_x):
        species = [i for i in self.data['Species']][[i for i in self.data[self.x]].index(c_x)]
        return species

    def TestProbability(self, Prediction):
        Test = []
        f_Test = []

        # print len([p for p in self.test['Species']])
        # print len(Prediction)

        i_ = 0
        for i in Prediction:
            #print [p for p in self.test['Species']][Prediction.index(i)]
            #print Prediction.index(i)
            #print [p for p in self.test['Species']][i_]

            if [p for p in self.test['Species']][i_] == i:
                Test.append(1)
            else:
                Test.append(0)
            i_ += 1

        for t in Test:
            if t != 0:
                f_Test.append(t)

        # print len(f_Test)
        # print len(Test)
        # print float(len(f_Test)) / float(len(Test))

        return float(len(f_Test)) / float(len(Test)) * 100



    def KNearestNeigbours(self):
        species = []
        d_s = []

        for i in self.test[self.x]:
            distances = [self.DistanceBetween(d, i) for d in self.train[self.x]]
            nearest = [[x for x in self.train[self.x]][i] for i in [distances.index(s) for s in sorted(distances)[:self.n]]]
            for n_i in nearest:
                d_s.append((i, n_i))
            nearest_species = [self.GetSpecies(x) for x in nearest]
            species.append(self.most_common(nearest_species))
            #species.append('setosa')

        self.d_s = d_s
        #self.plot(d_s)

        return [species, self.TestProbability(species)]

url = "https://vincentarelbundock.github.io/Rdatasets/csv/datasets/iris.csv"

# Instance = Learn("Sepal.Length", "Sepal.Width", 10, url)
# Instance.point = (0,0)
#
# print Instance.KNearestNeigbours()
#
# Instance = Learn("Petal.Length", "Petal.Width", 10, url)
# Instance.point = (0,0)
#
# print Instance.KNearestNeigbours()

plot_list = []
probability_list = []
bar_names = []

for i in [i for i in combinations(["Sepal.Length", "Sepal.Width", "Petal.Length", "Petal.Width"], 2)]:
    Instance = Learn(i[0], i[1], 10, url)
    probability_list.append(Instance.KNearestNeigbours()[1])
    bar_names.append("{0} * {1}".format(i[0], i[1]))
    plot_list.append(Instance.plot())

output_file("lines.html")

bar_dict = {'values':probability_list, 'names':bar_names}
bar_df = pd.DataFrame(bar_dict)

bar_p = Bar(bar_df, 'names', values='values', title="Probabilities")
plot_list.append(bar_p)

grid = gridplot([plot_list])

save(grid)

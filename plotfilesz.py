#!/usr/bin/env python

'''
 Plots a PDF of all the file sizes within a directory by recursively
 walking the directory. This code demostrates the use of simple probability
 functions and plotting in python.

 For beter plotting directories containing movies or songs, it ignores
 some types of files with extensions specified in the invalidext set.
'''

import os
from sys import argv
from pylab import *
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde

def filename_filter(f):
  validext=('')
  invalidext=('.srt','.nfo','.sub','txt')
  return True
  #return f.endswith(validext) and (not f.endswith(invalidext))


def filesize_plot(rootpath):

  l=[]
  #l2=[]
  for root, dirs, files in os.walk(rootpath):
    #l2.extend([(f, os.path.getsize(root+"/"+f)/(1024.0*1024.0)) for f in files if filename_filter(f)])
    l.extend([os.path.getsize(root+"/"+f)/(1024.0*1024.0) for f in files if filename_filter(f)])
  
  #for a,b in l2:
  #  print b,a

  density = gaussian_kde(l)

  print len(l), min(l), max(l)
  # set the covariance_factor, lower means more detail
  density.covariance_factor = lambda : .25
  density._compute_covariance()

  xs = np.linspace(min(l), max(l), 2000)
  plt.xlabel('File size (MB)')
  plt.ylabel('density')
  plt.title('Probability density of files in ' + rootpath)
  plt.grid(True)
  plt.plot(xs,density(xs))
  #l.sort()  
  #plt.hist(l, bins=2000)
  plt.show()

filesize_plot(argv[1])


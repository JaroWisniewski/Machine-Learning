# -*- coding: utf-8 -*-
from __future__ import print_function

from time import time
import logging
import matplotlib.pyplot as plt
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.datasets import fetch_lfw_people

from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
from skimage.feature import canny
from sklearn.metrics.cluster import homogeneity_score, v_measure_score


print(__doc__)

# Display progress logs on stdout
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')


###############################################################################
# Download the data, if not already on disk and load it as numpy arrays

lfw_people = fetch_lfw_people(min_faces_per_person=70)

# introspect the images arrays to find the shapes (for plotting)
n_samples, h, w = lfw_people.images.shape

# for machine learning we use the 2 data directly (as relative pixel
# positions info is ignored by this model)

X = lfw_people.data  
n_features = X.shape[1]

# the label to predict is the id of the person
y = lfw_people.target
target_names = lfw_people.target_names
n_classes = target_names.shape[0]

print("Total dataset size:")
print("n_samples: %d" % n_samples)
print("n_features: %d" % n_features)
print("n_classes: %d" % n_classes)

###############################################################################
# Split into a training set and a test set using a stratified k fold

# split into a training and testing set
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25)


###############################################################################
# Train a K- Means clustering model

print("Fitting the K Means clustering to the training set")

from sklearn.cluster import KMeans
kmeans = KMeans(init = 'k-means++', n_clusters=n_classes, n_init=30).fit(X_train, y_train)


###############################################################################
# Quantitative evaluation of the model quality on the test set

print("Predicting people's names on the test set")
t0 = time()
y_pred = kmeans.fit_predict(X_test, y_test)
print("done in %0.3fs" % (time() - t0))
print("Unique labels: {}".format(np.unique(y_pred)))

print("Number of points per cluster = {}".format(np.bincount(y_pred+1)))
print("Homogeneity score = {}".format(homogeneity_score(y_pred, y_test)))
print("V-Measure score = {}".format(v_measure_score(y_pred, y_test)))
print(classification_report(y_test, y_pred, target_names=target_names))
print(confusion_matrix(y_test, y_pred, labels=range(n_classes)))

###############################################################################
# Train a Agglomerative Clustering clustering model

from sklearn.cluster import AgglomerativeClustering

print("Fitting the Agglomerative Clustering to the training set")

for linkage in ('ward', 'average', 'complete'):
    clustering = AgglomerativeClustering(linkage=linkage, n_clusters=n_classes)
    t0 = time()
    clustering.fit(X_train, y_train)
    print("Linkage {}".format(linkage))
    y_pred = clustering.fit_predict(X_test, y_test)
    print(classification_report(y_test, y_pred, target_names=target_names))
    print(confusion_matrix(y_test, y_pred, labels=range(n_classes))) 
    print("Homogeneity score = {}".format(homogeneity_score(y_pred, y_test)))
    print("V-Measure score = {}".format(v_measure_score(y_pred, y_test)))
###############################################################################
# Train a K- Means clustering model using preprocessed data
print("Pre processing using edge detection....")

Z = lfw_people.data

for i in range(n_samples):
    image = Z[i].reshape(h, w)
    edges = canny(image, sigma=3)
    Z[i] = edges.reshape(h*w)

X_train, X_test, y_train, y_test = train_test_split(
    Z, y, test_size=0.25)
    
kmeans = KMeans(init = 'k-means++', n_clusters=n_classes, n_init=30).fit(X_train, y_train)


###############################################################################
# Quantitative evaluation of the model quality on the test set

print("Predicting people's names on the test set")
t0 = time()
y_pred = kmeans.fit_predict(X_test, y_test)
print("done in %0.3fs" % (time() - t0))
print("Unique labels: {}".format(np.unique(y_pred)))

print("Number of points per cluster using edge detection pre processing= {}".format(np.bincount(y_pred+1)))
print(classification_report(y_test, y_pred, target_names=target_names))
print(confusion_matrix(y_test, y_pred, labels=range(n_classes)))
print("Homogeneity score = {}".format(homogeneity_score(y_pred, y_test)))
print("V-Measure score = {}".format(v_measure_score(y_pred, y_test)))

for cluster in range(max(y_pred) +1):
    mask = y_pred == cluster
    n_images = np.sum(mask)
    fig, axes = plt.subplots(1, n_images, figsize=(n_images * 1.5, 4), subplot_kw={'xticks':(), 'yticks':()})
    figa = plt.gcf()
    figa.canvas.set_window_title("Clustering with edge detection - {}".format(cluster))
    for images, label, ax in zip(X_test[mask], y_test[mask], axes):
         ax.imshow(images.reshape((h, w)), cmap=plt.cm.gray)
         ax.set_title(lfw_people.target_names[label].split()[-1])
         
plt.show()

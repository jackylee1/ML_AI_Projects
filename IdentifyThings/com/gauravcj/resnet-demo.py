import mxnet as mx
import numpy as np
import cv2,sys,time
from collections import namedtuple
from pygame import mixer
import subprocess


cameraimagefile = "image.jpg"

def capturePicture():
    print("Capturing picture...")
    subprocess.call (["fswebcam","-r", "640x480", cameraimagefile])
    #subprocess.call(["imagesnap","-w","1", cameraimagefile])
        

def loadModel(modelname):
        t1 = time.time()
        sym, arg_params, aux_params = mx.model.load_checkpoint(modelname, 0)
        t2 = time.time()
        t = 1000*(t2-t1)
        print("Loaded in %2.2f milliseconds" % t)
        arg_params['prob_label'] = mx.nd.array([0])
        mod = mx.mod.Module(symbol=sym)
        mod.bind(for_training=False, data_shapes=[('data', (1,3,224,224))])
        mod.set_params(arg_params, aux_params)
        return mod

def loadCategories():
        synsetfile = open('synset.txt', 'r')
        synsets = []
        for l in synsetfile:
                synsets.append(l.rstrip())
        return synsets

def prepareNDArray(filename):
        img = cv2.imread(filename)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (224, 224,))
        img = np.swapaxes(img, 0, 2)
        img = np.swapaxes(img, 1, 2)
        img = img[np.newaxis, :]
        return mx.nd.array(img)
      
def predict(filename, model, categories, n):
        array = prepareNDArray(filename)
        Batch = namedtuple('Batch', ['data'])
        t1 = time.time()
        model.forward(Batch([array]))
        t2 = time.time()
        t = 1000*(t2-t1)
        print("Predicted in %2.2f millsecond" % t)
        prob = model.get_outputs()[0].asnumpy()
        prob = np.squeeze(prob)
        sortedprobindex = np.argsort(prob)[::-1]
        topn = []
        for i in sortedprobindex[0:n]:
                topn.append((prob[i], categories[i]))
        return topn

def init(modelname):
        model = loadModel(modelname)
        cats = loadCategories()
        return model, cats


if __name__ == '__main__':
    resnet152,c = init("resnet-152")
    
    while(True):
        capturePicture()
        print ("*** ResNet-152")
        print predict(cameraimagefile,resnet152,c,5)
        time.sleep(5)

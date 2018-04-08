# Note:  to run on the Raspberry Pi, hard-coded paths below must be changed.
# Note:  the API endpoint is also hard-coded below.

import os, glob, json, calendar, time, requests
import random
import librosa
import librosa.display
import matplotlib.pyplot as plt
# from keras.applications.vgg16 import preprocess_input
# from keras.utils import multi_gpu_model
import numpy as np
from keras import metrics, optimizers
from keras.applications.vgg16 import VGG16
from keras.layers import Dense, Dropout, Flatten, Input
from keras.models import Sequential, Model
from keras.preprocessing import image
# from scipy.io import wavfile
from sklearn.preprocessing import scale

user_id = "zPpgsPmGSVculcMmCXZ4FqFW"
api_endpoint = "http://lyvia.herokuapp.com/telemetry"
training_data_dir = 'C:/Users/home/boston/lyvia/model/boston/training/'
validation_data_dir ='C:/Users/home/boston/lyvia/model/boston/validation/'
num_layers_to_freeze = 15
timestamp = float(calendar.timegm(time.gmtime()))

# Adapted from Rivas' example:
def get_top_k_predictions(preds, label_map, k=5, print_flag=False):
    sorted_array = np.argsort(preds)[::-1]
    top_k = sorted_array[:k]
    label_map_flip = dict((v, k) for k, v in label_map.iteritems())

    y_pred = []
    for label_index in top_k:
        if print_flag:
            print
            "{} ({})".format(label_map_flip[label_index], preds[label_index])
        y_pred.append(label_map_flip[label_index])

    return y_pred

def save_melspectrogram(file_name,
                        sampling_rate=44100):
    """ Save spectrogram"""
    path_to_file = file_name
    data, sr = librosa.load(path_to_file,
                            sr=sampling_rate,
                            mono=True)
    data = scale(data)

    melspec = librosa.feature.melspectrogram(y=data, sr=sr, n_mels=128)
    # Convert to log scale (dB) using the peak power (max) as reference
    # per suggestion from Librbosa: https://librosa.github.io/librosa/generated/librosa.feature.melspectrogram.html
    log_melspec = librosa.power_to_db(melspec, ref=np.max)
    librosa.display.specshow(log_melspec, sr=sr)
    plt.savefig(file_name.strip('.wav') + '.png')

# Three labels, [1,2,3]
for label in range(1, 51):
    for filename in glob.glob("{0}/{1}/*.wav".format(training_data_dir, str(label))):
        save_melspectrogram(filename, sampling_rate=44100)

batch_size = 50
epochs = 75

# dimensions of our images.
img_width, img_height = 224, 224

input_tensor = Input(shape=(224,224,3))

nb_training_samples = 1600
nb_validation_samples = 400

training_datagen = image.ImageDataGenerator(
    rescale=1./255)

training_generator = training_datagen.flow_from_directory(
    training_data_dir,
    target_size=(img_height, img_width),
    batch_size=batch_size)

validation_datagen = image.ImageDataGenerator(
    rescale=1./255)

validation_generator = validation_datagen.flow_from_directory(
    validation_data_dir,
    target_size=(img_height, img_width),
    batch_size=batch_size)

base_model = VGG16(weights='imagenet', include_top=False, input_tensor=input_tensor)

# Not sure if there are side effects here
base_model.summary()
top_model = Sequential()
top_model.add(Flatten(input_shape=base_model.output_shape[1:]))
top_model.add(Dense(256, activation='relu'))
top_model.add(Dropout(0.5))
top_model.add(Dense(50, activation='softmax'))
top_model.summary()
model = Model(inputs=base_model.input, outputs=top_model(base_model.output))
model.summary()

def top_5_accuracy(y_true, y_pred):
    return metrics.top_k_categorical_accuracy(y_true, y_pred, k=5)

for layer in model.layers[:num_layers_to_freeze]:
    layer.trainable = False

# use nesterov accelerated gradient descent ??
# optimizer=optimizers.SGD(lr=1e-4, momentum=0.9, decay=1e-6, nesterov=True)
model.compile(optimizer=optimizers.SGD(lr=1e-4, momentum=0.9),
                      loss='categorical_crossentropy',
                      metrics=['accuracy', top_5_accuracy])
# serialize model to JSON
model_json = model.to_json()
model_filename = "vgg16_model_{}_frozen_layers.json".format(num_layers_to_freeze)
# with open(model_filename, "w") as json_file:
#     json_file.write(model_json)

import pdb; pdb.set_trace()
model.fit_generator(
    training_generator,
    steps_per_epoch=nb_training_samples/batch_size,
    epochs=epochs) #,
    # validation_data=validation_generator,
    # validation_steps=nb_validation_samples/batch_size,
    # callbacks=[])
label_map = (training_generator.class_indices)

json = json.dumps(label_map)
f = open("label_map.json", "w")
f.write(json)
f.close()

# Choose a random time sample for the night
nightly_fourier_graphs = glob.glob(training_data_dir + "1/*.png")
img_path = random.choice(nightly_fourier_graphs)

img = image.load_img(img_path, target_size=(224, 224))
x = image.img_to_array(img)
x = np.expand_dims(x, axis=0) * 1. / 255
import pdb; pdb.set_trace()
preds = model.predict(x)[0]

top_3 = get_top_k_predictions(preds, label_map, k=3)

clusters_list =  sorted([int(x)*5 for x in top_3])
x,y,z =  [clusters_list[0], clusters_list[1]-clusters_list[0], clusters_list[2]-clusters_list[1]]
anomalous = x > 50

req = requests.post(api_endpoint,
                    json={"x":x, "y": y, "z":z,
                     "anomalous": anomalous,
                     "dt": timestamp,
                     "user_id": user_id})
import pandas as pd

import classification_utilities
from networks_setups import *
from sklearn.metrics import confusion_matrix

filename = 'training_data.csv'
testname = 'facies_vectors.csv'

facies_labels = ['SS', 'CSiS', 'FSiS', 'SiSh', 'MS', 'WS', 'D', 'PS', 'BS']
adjacent_facies = np.array([[1], [0, 2], [1], [4], [3, 5], [4, 6, 7], [5, 7], [5, 6, 8], [6, 7]])

TRAIN_RATIO = 0.3  # using the rule of thumb of 1/sqrt(num_input_variables)

training_data = pd.read_csv(filename)
test_data = pd.read_csv(testname)

# Combine and shuffle our data
base_data = test_data.append(training_data)

np.random.seed(8)
rand_index = np.random.permutation(np.arange(base_data.shape[0]))

# Split train/test set
sample_index = -1 * int(TRAIN_RATIO * float(base_data.shape[0]))

vals = base_data['Facies'].values[sample_index:]
vals -= 1
hot_vals = np.zeros((vals.size, vals.max() + 1))
hot_vals[np.arange(vals.size), vals] = 1
test_labels_T = tf.convert_to_tensor(hot_vals)

labels_w_noise, base_data = add_input_noise_from_facies(base_data, adjacent_facies)

all_data = cleanup_csv(base_data)
labels_T = tf.convert_to_tensor(labels_w_noise[:sample_index])

# Output data one hot between 1-9. Facies
y_ = tf.placeholder(tf.float32, shape=[None, NUM_FACIES])

# network setup
y, x, features_T, test_features_T = three_layer_network(all_data, sample_index, seed=10)

# loss function used to train
cross_entropy = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(y, y_))

# backprop
train_step = tf.train.AdamOptimizer(1e-3).minimize(cross_entropy)

# Accuracy calculations
correct_prediction = tf.equal(tf.argmax(y, 1), tf.argmax(y_, 1))
accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))

# session init
sess = tf.Session()
sess.run(tf.global_variables_initializer())

for i in range(20000):
    x_vals, y_labels, x_vals_t, y_labels_t = sess.run([features_T, labels_T, test_features_T, test_labels_T])

    train_data = {x: x_vals, y_: y_labels}
    _, train_acc = sess.run([train_step, accuracy], feed_dict=train_data)

    test_data = {x: x_vals_t, y_: y_labels_t}
    test_acc = sess.run(accuracy, feed_dict=test_data)

    if i % 1000 == 0:
        print('epoch', i / 1000)
        print('test acc', test_acc)
        print('train acc', train_acc, '\n')

real, predicted = y_labels, sess.run(y, feed_dict=train_data)
real_t, predicted_t = y_labels_t, sess.run(y, feed_dict=test_data)

real = np.argmax(real, axis=1)
predicted = np.argmax(predicted, axis=1)
real_t = np.argmax(real_t, axis=1)
predicted_t = np.argmax(predicted_t, axis=1)

conf = confusion_matrix(real, predicted)
conf2 = confusion_matrix(real_t, predicted_t)

print("\nModel Report")
print("-Adjacent Accuracy: %.6f" % (classification_utilities.accuracy_adjacent(conf, adjacent_facies)))
print("\nConfusion Matrix")

classification_utilities.display_cm(conf, facies_labels, display_metrics=True, hide_zeros=True)

print("\nTEST data")
print("\nConfusion Matrix")
print("-Adjacent Accuracy: %.6f" % (classification_utilities.accuracy_adjacent(conf2, adjacent_facies)))
classification_utilities.display_cm(conf2, facies_labels, display_metrics=True, hide_zeros=True)

validation = 'validation_data_nofacies.csv'
validation_data = pd.read_csv(validation)
v_data = cleanup_csv(validation_data)

final_predictions = sess.run(y, feed_dict={x: v_data.values})

# Get the final predictions and index back to 1-9
final_predictions = np.argmax(final_predictions, axis=1) + 1
validation_data['Facies'] = final_predictions
validation_data.to_csv('ARANZGeo/final_predictions.csv')

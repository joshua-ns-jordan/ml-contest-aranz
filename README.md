# ml-contest-aranz
Investigation into machine learning as part of the geological contest 
https://github.com/seg/2016-ml-contest/blob/master/index.ipynb

I will be using google's tensorflow library to try a variety of machine learning solutions to the problem. This choice is due to the flexibility and resources available with this library. It is also described as Numpy on steroids which should give some familiarity to myself. 
The goal is, given a csv file of wells with various measurements at each depth, predict the correct facie value for each depth. 

This readme is an record of the steps taken as I progress through this project.
 
## INSTALLATION
Install on windows using the anaconda package manager. This seems to be the only way to get all the dependencies to work properly. The installation [guide](https://www.tensorflow.org/get_started/os_setup#anaconda_installation) provided by google is reasonable.
 
## BENCHMARK 
There are 10 inputs and 9 potential facie values in our model. By random guess we should expect to get ~11% of answers correct (this is our lowest benchmark that all models must beat). The benchmark set by the contest is **41%**. The current highest result seems to be around **60%** accuracy. 
 
## DATA CLEANUP 
In order to use the csv files data we need to ensure that the input columns are regularised. In this case I have replaced the formation and well names with integer values, this will allow it to be an input into our model (as we cannot input a string). We also normalize the fields and replace missing values. 
The output (facie value) is also changed into a one-hot encoding rather than an integer, this allows for the result to be a probability of the correct facie. The result is then computed by taking the max probability index using the softmax algorithm. 
 
## IMPLEMENTATION 
As a first pass we use the train/test data sets given from the competition. We also copy the very basic MINST implementation given in the tensorflow tutorial. This consists of a basic regression matrix of the form:

y = x.W + b

Where W is the weights and b is the biases. These values are updated each iteration by the regression algorithm. We update by minimizing the cross-entropy between our predicted results y and our actual results y_.

The accuracy of our results are defined as the performance of the algorithm in classifying the test set correctly ie. y vs y_. 

### First pass 
As a first pass the basic MINST tutorial implementation was used. This uses a very basic gradient decent algorithm to calculate the weights. Using the GradientDecentOptimizer to minimize the cross-entropy and a learning rate of 1e-3 produced: **~19%** accuracy with non-convergence.

### Learning rate
Non-convergence indicates that we cannot find a local minimum, this can be due to a variety of reasons but a common one is that our learning rate is too high. Metaphorically this is that we are constantly jumping around with large steps meaning that we overshoot the minimum.

A basic solution to this is to reduce the learning rate, effectively taking smaller steps with each gradients change. Reducing the learning rate to 1e-6 resulted in convergence and a final accuracy of **22%**.

### Optimisation algorithm 
22% is very poor. One way to improve this is to use a different optimisation algorithm. Gradient decent is a rather limited algorithm and often struggles to find the global minimum. Taking cues from other contestants we instead will try the [ADAM optimizer] (https://arxiv.org/pdf/1412.6980.pdf). This is a more refined algorithm that implements exponential decay rate for the estimates. Using the Adam optimiser with a learning rate of 1e-5 over 20,000 iterations produced an accuracy of **45%**.  
The accuracy after 20,000 iterations seemed to be continuing to improve, to test this I increased the number of iterations to 120,000. This produced an accuracy of **48%**. After playing with the meta-parameters using the validation set, I found that a learning rate of 1e-3 for the ADAM optimizer produced a solution that converged quickly.

### Training and test data randomization 
The initial training/test data is not randomised, it is split by well name (and ordered by depth). It also has a test/training split of ~50/50. The lack of randomisation will lead to overfitting, this can be seen in other contestants results where the accuracy on their training set was ~80%, but the accuracy on the blind set plumetted down to ~55%. 

To combat this, we add the two datasets together and then randomise the index (using a seed for reproducibility). Then we split the data into 20% training, 80% test. After running over 15,000 iterations with a learning rate of 1e-3 the accuracy was **~49%**, the training data accuracy improved to *~63%*. 

Although this isn't much of an improvement in accuracy on the test set, the large difference in test/training accuracy indicates that we may, if anything, be underfitting.

### Use random initial weights 
Currently we are using zeros as our initial weight biases, instead we can initialise them to be random. Random or guassian noise is important so that if we have a local minimum near, for example, 0 we do not converage straight to this. The result of this was an unchanged accuracy, however the first epoch had a very low accuracy compared to an initialisation of zeros (which is expected if the solution weights are mainly zero). 

### Deep network 
Let's go deep with some [tricks] (http://lamda.nju.edu.cn/weixs/project/CNNTricks/CNNTricks.html).
The topography of the hidden layers in neural networks are a tricky problem and there is no real consensus for deciding. Instead the meta parameters are one of the main "levers" a ML researcher uses to improve performance. One point that seems to be agreed upon is that the more hidden layers in the network, the harder it becomes to train (for a variety of reasons). Larger layered networks also can tend to overfit. So as a first pass we will try with one hidden layer of n= 9 (based on the rule of thumb that the hidden layer size should be bounded by the input and output feature numbers). 
 
n == 10, @ 1e-3 and 20,000 iterations: **51%**, training set accuracy *84%*.  
n == 15 @1e-3 and 20,000 iterations: **50%**, training set accuracy *90%*.

The training accuracy is now looking like a reasonable figure, indicating that we are modeling or training set well. It also improves as we increase the number of parameters in the hidden layer. This is to be expected, as we are increasing the complexity of the model and thus we expect it to be able to model the training set almost perfectly given enough neurons. 

However as a result we are now experience significant underfitting in our model. One way to reduce underfitting increase the ratio of test/training data; basically give the model more data to work with.

### Training ratios and my confusion
After reading some more information of the training/test/validation [ratios] (http://stackoverflow.com/questions/13610074/is-there-a-rule-of-thumb-for-how-to-divide-a-dataset-into-training-and-validatio), it looks as though my ratio of test/train (and validation) should be inverted.

Using the approximate rule of thumb of:  
1/sqrt(# inputs) 

There should be 30% test data and 70% training, **not** 20% training and 80% test as I have been using. With this new ratio we get:
n1 == 15 @ 1e-3 and 20,000 iterations, **78%**, training set accuracy *84%*.

Using a two-layered network:
n1 == 25, n2 == 15 @1e-3 and 20,000 iterations, **80%**, training set accuracy *85%*.

Now we're getting somewhere! As expected the test accuracy has shot up to be much closer to the training accuracy; we are no longer underfitting. The difference between the test and the training set, combined with the precautions undertaken to randomise the data should mean that we are not overfitting.
 
 

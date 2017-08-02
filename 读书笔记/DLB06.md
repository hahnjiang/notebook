# Chapter 6 Deep Feedforward Networks 前馈神经网络
## 6.1 Example: Learning XOR
## 6.2 基于梯度学习
神经网络的学习过程和其他机器学习算法的学习过程都是一样的，即基于梯度学习。
神经网络因为模型结构复杂和非线性导致 Loss 函数不再是凸函数。这意味着神经网络用基于梯度的迭代优化器得到的是近似的极小值，而不是其他线性和凸优化问题得到的全局收敛的最小值。
凸优化问题不依赖初始值的选择，或者说从任意初值开始都可以收敛到最小值；神经网络使用的 SGD（随机梯度下降） 需要依赖初值的设定，并不能保证收敛。
DNN 所有的权重初值是很小的随机数，偏移初值是0或者很小的正数。
BP（反向传播）用来计算神经网络的梯度。
### 6.2.1 损失函数

$$\widehat{y}=W^{T}h+b$$

<img src="http://latex.codecogs.com/gif.latex?\widehat{y}=W^{T}h&plus;b" title="\widehat{y}=W^{T}h+b" />

![数学](http://latex.codecogs.com/gif.latex?%5Cwidehat%7By%7D%3DW%5E%7BT%7Dh&plus;b)


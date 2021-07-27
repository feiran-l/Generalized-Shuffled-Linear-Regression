# Generalized-Shuffled-Linear-Regression

#### Code for the ICCV 2021 paper: [Generalized Shuffled Linear Regression](https://drive.google.com/file/d/1Qu21VK5qhCW8WVjiRnnBjehrYVmQrDNh/view?usp=sharing)

![Teaser](teaser.png)



### Run for demo
##### For image registration and point cloud registration:
* Install necessary dependencies: ```$ pip3 install requirements.txt ```
* Run `img_registration.py` for the image registration demo, and `pcd_registration.py` for the point cloud registration one. 

##### For isometric shape matching:
* Open the `shape_matching` path in Matlab. R2019a or later is needed to use the `matchpairs` function to solve the LAP.
* Run `demo.m` for fun.
* This Matlab code is revised from the excellent work of [BCICP](https://github.com/llorz/SGA18_orientation_BCICP_code), please pay attention to citation.


### Related topic
The main limitation of our current implementation lies in time efficiency, which is dominated by the LAP solver. 
Some CUDA-based Hungarian algorithms like [this](https://github.com/rapidsai/cugraph) may help to address this problem. 



### Contact
Please feel free to raise an issue or email to [li.feiran@ist.osaka-u.ac.jp](li.feiran@ist.osaka-u.ac.jp) if you have any question regarding the paper or any suggestions for further improvements. 


### Citation
If you find this code is helpful, thanks for citing our work as
```
@inproceedings{li2021gslr,
title = {Generalized Shuffled Linear Regression},
author = {Feiran Li and Kent Fujiwara and Fumio Okura and Yasuyuki Matsushita},
booktitle = {IEEE/CVF International Conference on Computer Vision (ICCV)},
year = {2021}
}

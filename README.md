# rpistudio
A set of scripts/modules to control scientific experiments using the Raspberry PI

Currently, _rpistudio_ has only a main function: being a good tool to perform a scientific experiment I'm involved in. In its original idea, it should be a set of python scripts/modules that run on the Raspberry PI to control simple scientific experiments.

In my use case, _rpistudio_ is responsible for maintaining costant a temperature inside an enclosure (using a Peltier cell and an H-bridge) and measuring some ambient parameters.

After some refactoring and a bit of work, I plan to generalize some of its functions, in order to allow an easier use by other interested people (if any). Anyway, the phylosophy of the project is that you have to write some code to personalize _rpistudio_ for your use case (the fun part). _rpistudio_ will take care of handling under the hood some tedious tasks.


## Planned TODO

* Improve results saving with a more flexible solution (currently, it works just for my case)
* Setup a web application to launch and control the experiments


## Contacts
Please, use my GitHub email.



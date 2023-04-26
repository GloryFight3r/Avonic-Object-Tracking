Q1 - What should the API look like
A1 - HTTP requests.

Q2 - What is the camera's API?
A2 - One week to write our own camera API. Advised to do so. Team connect ceiling(sennheiser) "https://nl-nl.sennheiser.com/tcc2"

Q2** - Story for the camera/microphone usage.
A2** - Improve indication by installing cameras at the end of the lecture hall and having the microphone at the beggining of the lecture hall. Becasue we are using this microphone its easier to capture the location. It is a problem having to zoom in/out every time a different person is speaking. A lot of universities are having the microphone already. Track only one speaker who is speaking. If there is an interactive session and the camera needs to detect who is speaking. Detecting then is much more complicated. Using the microphone you can detect the person who is speaking. It will require callibration since there are two environments(camera/microphone). The camera needs to understand the position. If you understand the environment that is given by the microphone and you can translate it  to the camera, then you just need to give the coordinates in a different way. That has to be done in the raspberry, since we can not program neither the microphone, nor the camera. 

Q3 - What should we use for the project?
A3 - Program in python, make it compatible with different device.

Q2* - Is there a documentation for the microphone?
A2* - Yes, huge documentation for the microphone is provided

Q4 - Are there any pipeline rules you would like to use/recommend to use, for good integration with your systems? (there was something on API - like use Flask)
A4 - Good documentation will certainly help. We use gitlab, they use github, so it has to integrate. If we can create the same pipeline for github, it would be helpful. But it is not mandatory. It will be helpful :). It should not be that difficult. Just make sure we document it well. 

Q4* - Should the project be a flask project?
A4* - It's up to us. The callibration idea should already be very challenging. Flask is just a framework, so it does not really matter. The user interface is not necessarily needed, but Ali believes we already have another challenge. UI is also a challenge, so it might take time. The project does not have to follow the directory structure Ali's team has.

Q5 - What's the microphone and what available resources for it exist
A5 - Well written documentation written for it.

Q6 - Django or Flask directory structure?
A6 - No, we don't need to follow their directory structure.

Q7 - Are there any limittataions of the system on shich the application is going to be deployed?
A7 - *

Q8 - Will we have access to your repository/code?
A8 - We won't need it at all. Just the API which is online. Implement it ourselves as he mentioned. Remote working will be available. So we can access our development kit from home. 

Q9 - What are the relevant code bases and documentations we have to look at?
A9 - There are implementations online on avonics website. Ali will send us it too.

Q10 - Do we have to clone a repository or start with a blank one?
A10 - Start with a blank one.

Q11 - Can we be in the office every Friday from 9 to 17 (in addition to Wednesdays and Thursdays)?
A11 - Yes, in the mornings. Wednesday and Thursday is full day. Friday from 9 to 12. Friday/Wednesday Ali is online, the other day he is there. 

Q12 - Any schedule that Ali suggests?
A12 - 
      #First week:
        * Learn python. 
        * Do research on what we need and what we want to learn. 
        * Create a drive - notes(we took every meeting), requirements and diagrams. It is only to help us(for now). 
        * Look into the documentation of the camera and microphone.
      #Second week:
        * Screen of the camera. Navigate the camera. Make use of the API of the camera. 
        * Deadline is thursday morning.
      #Third week - fourth, fifth week?:
        * Get familiar with the voice device.
        * Implement API
      #Week eight/nine:
        * Have the callibration/whole project done.
      
Q13 - Additional features? Face detection? No jittering?
A13 - Whatever we can add(detection - frame the person nicely in the middle). It's up to us.

Q14 - Project related stuff?
A14 - Good documentation. Test coverage over 70%. Not only written in code, but also like a wiki.

Q15 - When should we come back with the combined requirement?
A15 - Whenever we wish.

Q16 - Can we get the camera earlier?
A16 - We can get it even today(26 apr). He will make a call if it is possible. If it is possible we will be taking it before five o'clock. Worst case is friday.

A17 - The device must also acknowledge that it has received information. Use postman and package sender.

Q18 - Tools for testing?
A18 - Pytest. Pytest gives your more freedom(not sticking to OOP). For example you have a method and want to test its boundaries. In java you need to create a couple of tests. 

Q19 - Any metrics?
A19 - Using VSCode you can create configuration and share it with eachother. You can implement black(https://pypi.org/project/black/) and iSort(https://pycqa.github.io/isort/). Put them into the CI/CD, or just before pushing. They will run throught the whole code, making sure everything is well stacked. 

#Additional info:
  * Documentation for the camera.
  * Camera model - CM-70 - https://avonic.com/product/cm70-ip-w/
  * Two ways to communicate with the camera. IP/TCP. Send a request on its own ip. Or send a TCP package(using visca). Visca is faster and there is already a lot of documentation that we can find adjust a bit and make us of. Its very easy to use curl.
  * Make sure to learn a lot of virtual environments. Not advised to use conda. Venv and docker. 
  * Next Wednesday unbox the microphone.

# Next meeting:
  Regular meeting day. Thursday 10am.

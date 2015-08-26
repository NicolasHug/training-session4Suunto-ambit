# training-session4Suunto-ambit                                                 
A Python tool that helps you plan your training sessions for the Suunto Ambit watch (with intervals!)                                                         
                                                                                
What you need                                                                   
-------------                                                                   
                                                                                
You'll need Python (2 or 3) and the [Python Lex-Yacc](http://www.dabeaz.com/ply/) package. Just copy the `mly` folder in the main directory and you're good to go.                                       
                                                                                
                                                                                
How it works                                                                    
------------                                                                    
                                                                                
Run `python generateCode.py example.txt` to get a good grasp of it.             
                                                                                
Basically, all you need is write a small training session script as this one:   
        # warmup until lap button is pressed, with target at 70% of your max HR 
        run indefinitely at 70 % (wu);                                          
                                                                                
        # intervals :) !                                                        
        # The watch will automatically switch between the 'fast' and 'slow'     
        # without requiring you to press the lap button                         
        repeat 10 times {                                                       
          run 1m30s at 15 kmh +- 0.5 (fast); # 0.5 kmh with margin              
          run 1m0s at 10 kmh +- 1 (slow); # 1 kmh margin                        
        };                                                                      
                                                                                
        run 4.5 km (cd); # cooldown for 4.5 km, without any target              
                                                                                
and you'll get two output, each one being the source code of a Movescount app.  
                                                                                
The first app is the 'remaining app', telling you how much you have to go to    
complete the current training step. 'How much' is either a time in seconds or a 
distance in km. The watch will beep between each step.                          
                                                                                
The second  app is the 'target' app, that tells you if you're running higher or 
lower than your target, which is either a speed in km/h or a percentage of your 
maximum heart rate.         

For the two Movescount app, you will need to define four variables with the     
following initial values:                                                       
                                                                                
| Variable           | Value |                                                  
| ------------------ | ----- |                                                  
| current_lap_number | 1     |                                                  
| step               | 0     |                                                  
| last_step_duration | 0     |                                                  
| last_step_distance | 0     |                                                  
                                                                                
Syntax of a training session script                                             
-----------------------------------                                             
                                                                                
A training session script is a sequence of running steps that can be repeated.  
Each step must be ended by a semicolon character.                               
                                                                                
`run DURATION_OR_DISTANCE [at TARGET [+- MARGIN]] [(text)]; # comment`          
                                                                                
`repeat NUMBER times { run... ; run ...; ...};`                                 
                                                                                
DURATION_OR_DISTANCE is either a duration in minutes and seconds (ex:`3m5s`     
meaning 3 minutes and 5 seconds), or a distance in km (ex: `3km` or `3.5 km`).  
It can also be `indefinitely`. In that case, the watch will wait for you to     
press the lap button to switch to the next state.                               
                                                                                
A target can be specified. It is either a speed in kmh (ex: `12.5 kmh`) or a    
percentage of your maximum heart rate (ex: `70%`). If you're running lower than 
your target, the 'target app' will display '--'. It will display '++' if you're 
running higher, and 'ok' if you're doing well.                                  
                                                                                
With the target, you can specify a given margin (ex: `+- 2`). If your target    
was 10kmh with a margin of 2 the watch will tell you you're ok as long as you  
run between 8 and 12 kmh.                                                       
                                                                                
You can add a small text between parenthesis at the end of you're running step. 
This will be translated as the prefix of the 'duration app'.                    
                                                                                
Note 1: nested `repeat` structures are not supported.                           
Note 2: Happy running!!           

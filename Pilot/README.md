## RecolagEval

### Alpha
The alpha directory contains the very first data collection.

| variables                         | easy  | medium| hard  |
|---|----|---|---|
|  grouped pieces                   | 12    | 12    | 15    |   
|  similar pieces per group         | 3     | 3     | 3     |   
|  random pieces                    | 4     | 5     | 6     |   
|  shared characteristics per group | 2     | 3     | 4     |   


#### extract information

`python reader.py alpha/logs/`


### Beta
The beta directory contains a second iteration of alpha where the difficoulty level of the hard boards has been increased.  

| variables                         | easy  | medium| hard  |
|---|----|---|---|
| grouped pieces                    | 12    | 12    | 16    |   
| similar pieces per group          | 3     | 3     | 4     |   
| random pieces                     | 4     | 5     | 6     |   
| shared characteristics per group  | 2     | 3     | 4     |  

* to ignore: 1929, 1940, 1941

The beta study is divided into two subdirectories:
* `hint`: the participants who were shown the hint image at the beginning of the study
* `no_hint`: the participants were not shown any hint

#### extract information

* `python reader.py beta/no_hint/`
* `python reader.py beta/hint/`
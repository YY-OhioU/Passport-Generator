# Passport Generation
## How to Use
### Install libraries
`pip install -r requirements.txt`

### Run code
Code will generate images with annotations.
Annotations will be organized in a json lines format in `ground_truth.jsonl`
```
usage: python main.py [-h] [-n NUMBER] [-o OUTPUT] [-b]

Generate fake passport images

options:
  -h, --help            show this help message and exit
  -n NUMBER, --number NUMBER
                        num of images
  -o OUTPUT, --output OUTPUT
                        output directory
  -b, --bbox            draw bounding boxes
  -a, --augment         Augment data. Perform transformations to images
```
`OUTPUT` folder needs to be created before the execution of this script

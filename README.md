# Open Targets Croissant exporter 🥐

This is the Open Targets [Croissant](https://docs.mlcommons.org/croissant/docs/croissant-spec.html) exporter currently under early development.


## Run dockerise version

```
docker build --tag 'ot_croissant' .
docker run -it 'ot_croissant'
```

## Usage

```
usage: ot_croissant [-h] --output OUTPUT -d DATASET

options:
  -h, --help            show this help message and exit
  --output OUTPUT       Output file path
  -d DATASET, --dataset DATASET
                        Dataset to include
```
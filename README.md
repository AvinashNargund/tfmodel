# tfmodel

[![CircleCI](https://circleci.com/gh/sfujiwara/tfmodel.svg?style=svg)](https://circleci.com/gh/sfujiwara/tfmodel)
[![MIT License](http://img.shields.io/badge/license-MIT-blue.svg?style=flat)](LICENSE)

This module includes pre-trained models converted for [TensorFlow](https://www.tensorflow.org/).

## Requirements

tfmodel requires nothing but TensorFlow.
Other libraries in [requirement.txt](requirements.txt) are required only for unit tests or examples.

## Installation

```
pip install git+https://github.com/sfujiwara/tfmodel
```

## Models

### VGG 16

See [README_VGG16.md](README_VGG16.md).

## Unit Test

```
python -m unittest discover -v tests
```

## License

This module itself is released under MIT license.
**Note that weights of existing pre-trained models follow their licenses respectively**.
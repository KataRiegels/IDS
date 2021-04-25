# Emotional Sudoku

Emotional Sudoku is a game where you can play 4x4 sudoku using emotion detection from your webcam. The detected emotions are converted to emojis that are used to fill out the sudoku grid.

## Requirements

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install the required modules (excluding packages part of Python's standard library):

### OpenCV

```bash
pip install cv2
```

### NumPy

```bash
pip install numpy
```

### TensorFlow

```bash
pip install tensorflow
```

or

```bash
pip install tf-nightly
```

### curses for Windows

```bash
pip install windows-curses
```

## Usage

Running the program for default webcam:

```bash
python emotionalsudoku.py
```

Running the program for specific webcam:

(substitute camNo with the number of your preferred camera)

```bash
python emotionalsudoku.py -c camNo
```

## Authors

Kata Mitzie Riegels<br>
Jonatan Heine Langer<br>
Matthias Kaas-Mason<br>
Stine Fohrmann

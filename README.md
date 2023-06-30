# Image-Search-App
A Tkinter based Desktop app to make image search.


## How to use ?

### Without Python

If you don't have Python installed on your system, you can use the executable file provided in the `executable_file` folder. Follow these steps:

1. Clone the repository using the command:
```shell
git clone https://github.com/abdulanzil/Image-Search-App
```
2. Navigate to the folder `Image-Search-App`
3. Navigate to the `executable_file` folder.
4. Run the `ImageSearchApp.exe` file.

### With Python

If you have Python installed, you can run the application using the following steps:

1. Clone the repository using the command:
```shell
git clone https://github.com/abdulanzil/Image-Search-App
```
2. Navigate to the folder `Image-Search-App`
3. Install the following python packages:
```shell
pip install opencv-python
pip install Pillow
```
4. Run the python file using the command:
```shell
python ImageSearchApp.py
```


## Limitations

1. __Performance with large datasets:__ When dealing with a significant number of files and folders, the search process may experience reduced performance.
2. __Accuracy of image similarity:__ Although the image search algorithm employed in this project performs reasonably well, it may occasionally return images that are not truly similar. Similarly, some relevant images might not appear in the search results. Efforts are being made to overcome these issues in the future updates.
3. __No facial recognition feature:__ This project does not incorporate facial recognition capabilities.
4. __Compatibility with image formats:__ The project supports only common image formats such as JPG, JPEG and PNG.
5. __Operating system compatibility:__ While efforts have been made to ensure cross-platform compatibility, the project has primarily been tested on Windows operating system. There may be variations in behavior or compatibility on different platforms, and some features may not work as expected.

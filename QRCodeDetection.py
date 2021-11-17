
from matplotlib import pyplot
from matplotlib.patches import Rectangle

import imageIO.png


def createInitializedGreyscalePixelArray(image_width, image_height, initValue = 0):

    new_array = [[initValue for x in range(image_width)] for y in range(image_height)]
    return new_array


# this function reads an RGB color png file and returns width, height, as well as pixel arrays for r,g,b
def readRGBImageToSeparatePixelArrays(input_filename):

    image_reader = imageIO.png.Reader(filename=input_filename)
    # png reader gives us width and height, as well as RGB data in image_rows (a list of rows of RGB triplets)
    (image_width, image_height, rgb_image_rows, rgb_image_info) = image_reader.read()

    print("read image width={}, height={}".format(image_width, image_height))

    # our pixel arrays are lists of lists, where each inner list stores one row of greyscale pixels
    pixel_array_r = []
    pixel_array_g = []
    pixel_array_b = []

    for row in rgb_image_rows:
        pixel_row_r = []
        pixel_row_g = []
        pixel_row_b = []
        r = 0
        g = 0
        b = 0
        for elem in range(len(row)):
            # RGB triplets are stored consecutively in image_rows
            if elem % 3 == 0:
                r = row[elem]
            elif elem % 3 == 1:
                g = row[elem]
            else:
                b = row[elem]
                pixel_row_r.append(r)
                pixel_row_g.append(g)
                pixel_row_b.append(b)

        pixel_array_r.append(pixel_row_r)
        pixel_array_g.append(pixel_row_g)
        pixel_array_b.append(pixel_row_b)

    return (image_width, image_height, pixel_array_r, pixel_array_g, pixel_array_b)

# This method packs together three individual pixel arrays for r, g and b values into a single array that is fit for
# use in matplotlib's imshow method
def prepareRGBImageForImshowFromIndividualArrays(r,g,b,w,h):
    rgbImage = []
    for y in range(h):
        row = []
        for x in range(w):
            triple = []
            triple.append(r[y][x])
            triple.append(g[y][x])
            triple.append(b[y][x])
            row.append(triple)
        rgbImage.append(row)
    return rgbImage
    

# This method takes a greyscale pixel array and writes it into a png file
def writeGreyscalePixelArraytoPNG(output_filename, pixel_array, image_width, image_height):
    # now write the pixel array as a greyscale png
    file = open(output_filename, 'wb')  # binary mode is important
    writer = imageIO.png.Writer(image_width, image_height, greyscale=True)
    writer.write(file, pixel_array)
    file.close()

def computeRGBToGreyscale(pixel_array_r, pixel_array_g, pixel_array_b, image_width, image_height):
    
    greyscale_pixel_array = createInitializedGreyscalePixelArray(image_width, image_height)
    
    for i in range(image_height):
        for j in range(image_width):

            value = 0.299 * pixel_array_r[i][j] + 0.587 * pixel_array_g[i][j] + 0.114 * pixel_array_b[i][j]
            greyscale_pixel_array[i][j] = round(value)
            
    return greyscale_pixel_array

def scaleTo0And255AndQuantize(pixel_array, image_width, image_height):
    greyscale_pixel_array = createInitializedGreyscalePixelArray(image_width, image_height)
    minimum = pixel_array[0][0]
    maximum = minimum

    for i in pixel_array:

        if min(i) < minimum:
            minimum = min(i)

        if max(i) > maximum:
            maximum = max(i)

    if maximum == minimum:
        return greyscale_pixel_array
        
    else:

        for i in range(len(pixel_array)):
            for j in range(len(pixel_array[0])):
    
                greyscale_pixel_array[i][j] = round((pixel_array[i][j]-minimum)/(maximum-minimum)*255)

    return greyscale_pixel_array
    

def computeVerticalEdgesSobelAbsolute(pixel_array,image_width,image_height):

    array = createInitializedGreyscalePixelArray(image_width, image_height)
    sobel = [[1, 0, -1],
             [2, 0, -2],
             [1, 0, -1]]

    for i in range(1, image_height - 1):
        for j in range(1, image_width - 1):
            res = 0.0
            for k in range(3):
                for l in range(3):
                    res = res + (float(pixel_array[i + 1 - k][j + 1 - l]) * float(sobel[k][l]))
            array[i][j] = abs(res / 8.0)

    return array

def computeHorizontalEdgesSobelAbsolute(pixel_array,image_width,image_height):

    array = createInitializedGreyscalePixelArray(image_width, image_height)
    sobel = [[1, 2, 1],
             [0, 0, 0],
             [-1, -2, -1]]

    for i in range(1, image_height - 1):
        for j in range(1, image_width - 1):
            res = 0.0
            for k in range(3):
                for l in range(3):
                    res = res + (float(pixel_array[i + 1 - k][j + 1 - l]) * float(sobel[k][l]))
            array[i][j] = abs(res / 8.0)

    return array

def computeEdgeMagnitude(pixel_array, image_width, image_height):

    array = createInitializedGreyscalePixelArray(image_width, image_height)
    sobel1 = [[1, 0, -1],
             [2, 0, -2],
             [1, 0, -1]]
    
    sobel2 = [[1, 2, 1],
             [0, 0, 0],
             [-1, -2, -1]]

    for i in range(1, image_height - 1):
        for j in range(1, image_width - 1):
            res = 0.0
            res2= 0.0
            for k in range(3):
                for l in range(3):
                    res = res + (float(pixel_array[i + 1 - k][j + 1 - l]) * float(sobel1[k][l]))
                    res2 = res2 + (float(pixel_array[i + 1 - k][j + 1 - l]) * float(sobel2[k][l]))
            array[i][j] = abs(res / 8.0) + abs(res2 / 8.0)

    return array
    

def computeBoxAveraging3x3(pixel_array,image_width,image_height):
    
    array = createInitializedGreyscalePixelArray(image_width, image_height) 
    
    for i in range(1, image_height-1): 
        for j in range(1, image_width-1): 
            
            array[i][j] = pixel_array[i-1][j-1] + pixel_array[i-1][j] + pixel_array[i-1][j+1]
            
            array[i][j] += pixel_array[i][j-1] + pixel_array[i][j] + pixel_array[i][j+1] 
            array[i][j] += pixel_array[i+1][j-1] + pixel_array[i+1][j] + pixel_array[i+1][j+1] 
            
            array[i][j] = round((array[i][j])/9, 3) 
            
    return array 

def computeThresholdGE(pixel_array, threshold_value, image_width, image_height):
    threshold = []
    
    for i in range(image_height):
        array = []
        for j in range(image_width):
            if(pixel_array[i][j] < threshold_value):
                array.append(0)
            else:
                array.append(255)
                
        threshold.append(array)
        
    return threshold

def main():
    filename = "./images/covid19QRCode/poster1small.png"

    # we read in the png file, and receive three pixel arrays for red, green and blue components, respectively
    # each pixel array contains 8 bit integer values between 0 and 255 encoding the color values
    (image_width, image_height, px_array_r, px_array_g, px_array_b) = readRGBImageToSeparatePixelArrays(filename)


    pixel_array = (computeRGBToGreyscale(px_array_r, px_array_g, px_array_b, image_width, image_height)) #RGB to GreyScale
    vert = computeVerticalEdgesSobelAbsolute(pixel_array,image_width,image_height) #Vertical Edge Computation
    horz = computeHorizontalEdgesSobelAbsolute(pixel_array,image_width,image_height) #Horizontal Edge Computation
    edgeMagnitude = (computeEdgeMagnitude(pixel_array, image_width, image_height)) #Edge Magnitude computation
    
    smooth1 = computeBoxAveraging3x3(edgeMagnitude,image_width,image_height) #Smoothing of Edge Magnitude (8 times)
    smooth2 = computeBoxAveraging3x3(smooth1,image_width,image_height)
    smooth3 = computeBoxAveraging3x3(smooth2,image_width,image_height)
    smooth4 = computeBoxAveraging3x3(smooth3,image_width,image_height)
    smooth5 = computeBoxAveraging3x3(smooth4,image_width,image_height)
    smooth6 = computeBoxAveraging3x3(smooth5,image_width,image_height)
    smooth7 = computeBoxAveraging3x3(smooth6,image_width,image_height)
    smooth8 = computeBoxAveraging3x3(smooth7,image_width,image_height)
    
    pyplot.imshow(smooth8, cmap='gray')
    scaled = (scaleTo0And255AndQuantize(smooth8, image_width, image_height)) #Scaling to 0 and 255 (and quantize)
    pyplot.imshow(scaled, cmap='gray')
    thresholding = computeThresholdGE(scaled, 70, image_width, image_height) #Threshold Operation (using threshold value of 70)
    pyplot.imshow(thresholding, cmap='gray')
    

    # get access to the current pyplot figure
    axes = pyplot.gca()
    # create a 70x50 rectangle that starts at location 10,30, with a line width of 3
    rect = Rectangle( (10, 30), 70, 50, linewidth=3, edgecolor='g', facecolor='none' )
    # paint the rectangle over the current plot
    axes.add_patch(rect)

    # plot the current figure
    pyplot.show()



if __name__ == "__main__":
    main()

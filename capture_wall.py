import cv2
import numpy as np
import pygame


def get_contour(png_file):
    im = cv2.imread(png_file)
    # hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)

    # # Remember that in HSV space, Hue is color from 0..180. Red 320-360, and 0 - 30. Green is 30-100
    # # We keep Saturation and Value within a wide range but note not to go too low or we start getting black/gray
    # lower_green = np.array([30,140,0])
    # upper_green = np.array([100,255,255])

    # # Using inRange method, to create a mask
    # mask = cv2.inRange(hsv, lower_green, upper_green)

    # # We invert our mask only because we wanted to focus on the lady and not the background
    # mask[mask==0] = 10
    # mask[mask==255] = 0
    # mask[mask==10] = 255

    img_gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)

    # apply binary thresholding
    ret, thresh = cv2.threshold(img_gray, 250, 255, cv2.THRESH_BINARY)

    # contours, hierarchy = cv2.findContours(image=thresh, mode=cv2.RETR_TREE, method=cv2.CHAIN_APPROX_NONE)

    # detect the contours on the binary image using cv2.ChAIN_APPROX_SIMPLE
    contours1, hierarchy1 = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    return contours1[1], contours1[2]


class Wall:
    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

    def draw(self, win):
        pygame.draw.line(win, (255,255,255), (self.x1, self.y1), (self.x2, self.y2), 5)

def getWalls(png_file):
    walls = []

    # screen = get_screen()

    for contour in get_contour(png_file):
        length = len(contour)
        cnt = length // 50
        filtered_points = [contour[i][0] for i in range(length) if i % cnt == 0]
        for i in range(len(filtered_points)):
            next = i + 1 if i < len(filtered_points)-1 else 0
            wall = Wall(filtered_points[i][0], filtered_points[i][1], filtered_points[next][0], filtered_points[next][1])
            # wall.draw(screen)
            walls.append(wall)
    # pygame.display.update()
    return(walls)

WIDTH = 800
HEIGHT = 635

def get_screen():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("RACING DQN")
    screen.fill((0,0,0))
    back_image = pygame.image.load("AWS_track.png").convert()
    back_rect = back_image.get_rect().move(0, 0)

    screen.fill((0, 0, 0))
    screen.blit(back_image, back_rect)
    return screen

if __name__ == '__main__':

    png_file = 'AWS_track.png'
    contour1, contour2 = get_contour(png_file)
    im = cv2.imread(png_file)

    image_copy = im.copy()
    cv2.drawContours(image_copy, (contour1, contour2), contourIdx=-1, color=(0, 255, 0), thickness=2, lineType=cv2.LINE_AA)
    # visualize the binary image
    cv2.imshow('Binary image', image_copy)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    png_file
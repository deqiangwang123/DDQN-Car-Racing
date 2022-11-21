import pygame
import math
from Walls import Wall
from Goals import Goal

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Line:
    def __init__(self, pt1, pt2):
        self.pt1 = Point(pt1.x, pt1.y)
        self.pt2 = Point(pt2.x, pt2.y) 

class Car:
    def __init__(self, x, y):
        self.pt = Point(x, y)
        self.x = x
        self.y = y
        self.width = 14
        self.height = 30

        self.points = 0

        self.original_image = pygame.image.load("car.png").convert()
        self.image = self.original_image  # This will reference the rotated image.
        self.image.set_colorkey((0,0,0))
        self.rect = self.image.get_rect().move(self.x, self.y)

        self.angle = math.radians(90)
        self.soll_angle = self.angle

        self.dvel = 1
        self.vel = 0
        self.velX = 0
        self.velY = 0
        self.maxvel = 15 # before 15

        self.angle = math.radians(180)
        self.soll_angle = self.angle

        self.pt1 = Point(self.pt.x - self.width / 2, self.pt.y - self.height / 2)
        self.pt2 = Point(self.pt.x + self.width / 2, self.pt.y - self.height / 2)
        self.pt3 = Point(self.pt.x + self.width / 2, self.pt.y + self.height / 2)
        self.pt4 = Point(self.pt.x - self.width / 2, self.pt.y + self.height / 2)

        self.p1 = self.pt1
        self.p2 = self.pt2
        self.p3 = self.pt3
        self.p4 = self.pt4

        self.distances = []
        self.rays = []
        self.close_rays = []

    def distance(self, pt1, pt2):
        return(((pt1.x - pt2.x)**2 + (pt1.y - pt2.y)**2)**0.5)

    def rotate(self, origin,point,angle):
        qx = origin.x + math.cos(angle) * (point.x - origin.x) - math.sin(angle) * (point.y - origin.y)
        qy = origin.y + math.sin(angle) * (point.x - origin.x) + math.cos(angle) * (point.y - origin.y)
        q = Point(qx, qy)
        return q

    def rotateRect(self, pt1, pt2, pt3, pt4, angle):

        pt_center = Point((pt1.x + pt3.x)/2, (pt1.y + pt3.y)/2)

        pt1 = self.rotate(pt_center,pt1,angle)
        pt2 = self.rotate(pt_center,pt2,angle)
        pt3 = self.rotate(pt_center,pt3,angle)
        pt4 = self.rotate(pt_center,pt4,angle)

        return pt1, pt2, pt3, pt4

    class Ray:
        def __init__(self,x,y,angle):
            self.x = x
            self.y = y
            self.angle = angle

        def cast(self, wall):
            x1 = wall.x1 
            y1 = wall.y1
            x2 = wall.x2
            y2 = wall.y2

            vec = Car(0,0).rotate(Point(0,0), Point(0,-1000), self.angle)
            
            x3 = self.x
            y3 = self.y
            x4 = self.x + vec.x
            y4 = self.y + vec.y

            den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
                
            if(den == 0):
                den = 0
            else:
                t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / den
                u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / den

                if t > 0 and t < 1 and u < 1 and u > 0:
                    pt = Point(math.floor(x1 + t * (x2 - x1)), math.floor(y1 + t * (y2 - y1)))
                    return(pt)

    def action(self, choice):
        if choice == 0:
            pass
        elif choice == 1:
            self.turn(1)
        elif choice == 2:
            self.turn(-1)
        elif choice == 3:
            self.accelerate(self.dvel)
        elif choice == 4:
            self.accelerate(self.dvel)
            self.turn(1)
        elif choice == 5:
            self.accelerate(self.dvel)
            self.turn(-1)
        elif choice == 6:
            self.accelerate(-self.dvel)
        elif choice == 7:
            self.accelerate(-self.dvel)
            self.turn(1)
        elif choice == 8:
            self.accelerate(-self.dvel)
            self.turn(-1)
        pass
    
    def accelerate(self,dvel):
        dvel = dvel * 2

        self.vel = self.vel + dvel

        # if self.vel > self.maxvel:
        #     self.vel = self.maxvel

        if self.vel > 0:
            self.vel = 0

        if self.vel < -self.maxvel:
            self.vel = -self.maxvel

        # no backward
        # if self.vel < 0:
        #     self.vel = 0
              
    def turn(self, dir):
        self.soll_angle = self.soll_angle + dir * math.radians(15)
       
    def update(self):
        self.angle = self.soll_angle

        vec_temp = self.rotate(Point(0,0), Point(0,self.vel), self.angle)
        self.velX, self.velY = vec_temp.x, vec_temp.y

        self.x = self.x + self.velX
        self.y = self.y + self.velY

        self.rect.center = self.x, self.y

        self.pt1 = Point(self.pt1.x + self.velX, self.pt1.y + self.velY)
        self.pt2 = Point(self.pt2.x + self.velX, self.pt2.y + self.velY)
        self.pt3 = Point(self.pt3.x + self.velX, self.pt3.y + self.velY)
        self.pt4 = Point(self.pt4.x + self.velX, self.pt4.y + self.velY)

        self.p1 ,self.p2 ,self.p3 ,self.p4  = self.rotateRect(self.pt1, self.pt2, self.pt3, self.pt4, self.soll_angle)

        self.image = pygame.transform.rotate(self.original_image, 90 - self.soll_angle * 180 / math.pi)
        x, y = self.rect.center  # Save its current center.
        self.rect = self.image.get_rect()  # Replace old rect with new rect.
        self.rect.center = (x, y)

    def cast(self, walls):

        ray1 = self.Ray(self.x, self.y, self.soll_angle)
        ray2 = self.Ray(self.x, self.y, self.soll_angle - math.radians(30))
        ray3 = self.Ray(self.x, self.y, self.soll_angle + math.radians(30))
        ray4 = self.Ray(self.x, self.y, self.soll_angle + math.radians(45))
        ray5 = self.Ray(self.x, self.y, self.soll_angle - math.radians(45))
        ray6 = self.Ray(self.x, self.y, self.soll_angle + math.radians(90))
        ray7 = self.Ray(self.x, self.y, self.soll_angle - math.radians(90))
        ray8 = self.Ray(self.x, self.y, self.soll_angle + math.radians(180))

        ray9 =  self.Ray(self.x, self.y, self.soll_angle + math.radians(10))
        ray10 = self.Ray(self.x, self.y, self.soll_angle - math.radians(10))
        ray11 = self.Ray(self.x, self.y, self.soll_angle + math.radians(135))
        ray12 = self.Ray(self.x, self.y, self.soll_angle - math.radians(135))
        ray13 = self.Ray(self.x, self.y, self.soll_angle + math.radians(20))
        ray14 = self.Ray(self.x, self.y, self.soll_angle - math.radians(20))

        ray15 = self.Ray(self.p1.x,self.p1.y, self.soll_angle + math.radians(90))
        ray16 = self.Ray(self.p2.x,self.p2.y, self.soll_angle - math.radians(90))

        ray17 = self.Ray(self.p1.x,self.p1.y, self.soll_angle + math.radians(0))
        ray18 = self.Ray(self.p2.x,self.p2.y, self.soll_angle - math.radians(0))

        self.rays = []
        self.rays.append(ray1)
        self.rays.append(ray2)
        self.rays.append(ray3)
        self.rays.append(ray4)
        self.rays.append(ray5)
        self.rays.append(ray6)
        self.rays.append(ray7)
        self.rays.append(ray8)

        self.rays.append(ray9)
        self.rays.append(ray10)
        self.rays.append(ray11)
        self.rays.append(ray12)
        self.rays.append(ray13)
        self.rays.append(ray14)

        self.rays.append(ray15)
        self.rays.append(ray16)

        self.rays.append(ray17)
        self.rays.append(ray18)


        observations = []
        self.close_rays= []

        for ray in self.rays:
            temp = math.inf
            temp_pt = Point(0,0)
            for wall in walls:
                pt = ray.cast(wall)
                if pt:
                    # add the dist by different rays
                    dist = self.distance(Point(self.x, self.y),pt)
                    if dist < temp:
                        temp = dist
                        temp_pt = pt
            observations.append(temp)
            self.close_rays.append(temp_pt)
                # else:
                #     observations.append(10000)

        observations.append(self.vel / self.maxvel)
        observations.append(self.soll_angle)
        observations.append(self.dvel)
        return observations

    def collision(self, wall):

        line1 = Line(self.p1, self.p2)
        line2 = Line(self.p2, self.p3)
        line3 = Line(self.p3, self.p4)
        line4 = Line(self.p4, self.p1)

        x1 = wall.x1 
        y1 = wall.y1
        x2 = wall.x2
        y2 = wall.y2

        lines = []
        lines.append(line1)
        lines.append(line2)
        lines.append(line3)
        lines.append(line4)

        for li in lines:
            
            x3 = li.pt1.x
            y3 = li.pt1.y
            x4 = li.pt2.x
            y4 = li.pt2.y

            den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
            
            if(den == 0):
                den = 0
            else:
                t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / den
                u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / den

                if t > 0 and t < 1 and u < 1 and u > 0:
                    return(True)
        
        return(False)

    def cross_goal(self, goal):
        
        line1 = Line(self.p1, self.p3)

        vec = self.rotate(Point(0,0), Point(0,-50), self.angle)
        line1 = Line(Point(self.x,self.y),Point(self.x + vec.x, self.y + vec.y))

        x1 = goal.x1 
        y1 = goal.y1
        x2 = goal.x2
        y2 = goal.y2
            
        x3 = line1.pt1.x
        y3 = line1.pt1.y
        x4 = line1.pt2.x
        y4 = line1.pt2.y

        den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        
        if(den == 0):
            den = 0
        else:
            t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / den
            u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / den

            if t > 0 and t < 1 and u < 1 and u > 0:
                pt = math.floor(x1 + t * (x2 - x1)), math.floor(y1 + t * (y2 - y1))

                d = self.distance(Point(self.x, self.y), Point(pt[0], pt[1]))
                if d < 20:
                    #pygame.draw.circle(win, (0,255,0), pt, 5)
                    self.points += 1
                    return(True)

        return(False)

    def reset(self):

        self.x = 50
        self.y = 300
        self.velX = 0
        self.velY = 0
        self.vel = 0
        self.angle = math.radians(180)
        self.soll_angle = self.angle
        self.points = 0

        self.pt1 = Point(self.pt.x - self.width / 2, self.pt.y - self.height / 2)
        self.pt2 = Point(self.pt.x + self.width / 2, self.pt.y - self.height / 2)
        self.pt3 = Point(self.pt.x + self.width / 2, self.pt.y + self.height / 2)
        self.pt4 = Point(self.pt.x - self.width / 2, self.pt.y + self.height / 2)

        self.p1 = self.pt1
        self.p2 = self.pt2
        self.p3 = self.pt3
        self.p4 = self.pt4

    def draw(self, win):
        win.blit(self.image, self.rect)
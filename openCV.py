#IMPORT ALL LIBRARIES WE"LL NEED
import cv2
import mediapipe as mp #nickname for mediapipe
import serial
import time
import math


# Connect to Arduino
arduino = serial.Serial('COM4 ', 9600)  # Update and use Serial through port 4 (left corner fo laptop)
time.sleep(2) #set delay


# Setup MediaPipe
mp_hands = mp.solutions.hands#The hand-tracking module inside the mediapipe library
hands = mp_hands.Hands() #Activates the hand-tracking system inside Mediapipe, 21 landmarks across your fingers
#'Hands' when called creates a detector object, processes each video frame, and finds your hands and returns landmark values
mp_draw = mp.solutions.drawing_utils


cap = cv2.VideoCapture(0) #Begin capturing frames


def get_distance(handLms, point1, point2, w, h):
    x1, y1 = int(handLms.landmark[point1].x * w), int(handLms.landmark[point1].y * h) #Once frame gets values, we
    # Create a tuple with the calculated angles and measures between each of the points in order
    # to work from there, and we also turn them into pixel values
    x2, y2 = int(handLms.landmark[point2].x * w), int(handLms.landmark[point2].y * h)
    return math.hypot(x2 - x1, y2 - y1)#We close function and return the hypothenuse of the listed 21 landmark values


while True:
    success, img = cap.read() #Assign 'success' to cap.read() which reads one frame from the camera
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) 
    results = hands.process(img_rgb) #We take only one frame, read its values, mediapipe only supports RGB, so we turn the frame
    #into RGB


    #Declare default values to return at when no hand detected (or specified command)
    thumb_pwm = 0
    index_pwm = 0
    middle_angle = 0


    if results.multi_hand_landmarks: #If the command,'results.multi_hand_landmarks' is met, then we work with the next
        # lines, but what multi_hand_landmarks does is that it takes the 21 landmarks
        for handLms in results.multi_hand_landmarks: #look amongst all landmarks and assign the function 'img.shape' to have h and w
            h, w, _ = img.shape


            # Thumb openness
            thumb_dist = get_distance(handLms, mp_hands.HandLandmark.THUMB_TIP, mp_hands.HandLandmark.THUMB_IP, w, h)#We call the previous function we made
            # and give values to it through positional arguments (non-changing or assigned) to it, getting calculated values in return
            #What each argument means{
            #handsMLS: Hand landmark object #what it does: Contains all 21 finger points
            #mp_hands.HandLandmark.THUMB_TIP: Landmark index  # What it does: Tells MediaPipe which point to use
            #mp_hands.HandLandmark.THUMB_IP:Landmark index #What it does: Second point to measure against
            #w: image width #What it does:  Used to scale normalized coordinates to pixels, width
            #h: image height #What it does: Used to scale normalized coordinates to pixels, height
            #}
            thumb_pwm = int(min(max((thumb_dist - 10) * 10, 0), 255))
            #What this line does:
            #We store our calculations inside a new variable, 'int' ensures the result will be always a whole number,
            #then, 'min' ensures the value will never exceed 255, since Arduino can only handle as 255 PWM (motors)
            #'max' is a python function that looks for the highest value amongst a set of data, thumb_dist is our function we
            #already have a return value from, so we look for it's highest current value and substract 10 from it to
            #scale it down, e.g: position is 20,minus ten = 10, times ten = 100, this ensures extremely low
            # values such as '5' come out as '0' when, but values such as '11' will come out as '10', which
            # is the starting point if you want to name it like that.
            #Then the '0' is part of the max function, it ensures it can only come down to 0 MAXIMUM,
            #meaning if the value goes '-1' it will take it as a 0 because that's the maximum possible lowest output
            #Result: You get a value from 0-255 tracking where your thumb is, same goes for the next
            #Lines of code, except we call different fingers.
            # Index openness
            index_dist = get_distance(handLms, mp_hands.HandLandmark.INDEX_FINGER_TIP, mp_hands.HandLandmark.INDEX_FINGER_PIP, w, h)
            index_pwm = int(min(max((index_dist - 10) * 10, 0), 255))


            # Middle finger openness
            middle_dist = get_distance(handLms, mp_hands.HandLandmark.MIDDLE_FINGER_TIP, mp_hands.HandLandmark.MIDDLE_FINGER_PIP, w, h)
            middle_angle = int(min(max((middle_dist - 10) * 18, 0), 180))


            mp_draw.draw_landmarks(img, handLms, mp_hands.HAND_CONNECTIONS)


    # Send data to Arduino
    arduino.write(f"{thumb_pwm},{index_pwm},{middle_angle}\n".encode())
    #we make an f-string storing the now calculated values (e.g: thumb = 120, index_pwm = 60, middle_angle = 70,etc)
    #and use '\n' which creates a new line and tells arduino where the values end, then 'encode' turns the values
    #into bits, necessary for serial communication, then 'arduino.write' sends everything to arduino,
    #which splits the values, assigns themm, and uses them to control dcMotors and Servos
    print(f"Motor1: {thumb_pwm}, Motor2: {index_pwm}, Servo: {middle_angle}")
    #This is just a simple print statement to know the current values


    cv2.imshow("BioSync Gesture Control", img) #This shows the window with out live camera feed, current frame
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    #Wait until 'q' key is pressed in order to stop the live camera feed


cap.release()#when 'q' is pressed, this function lets go off the camera
arduino.close() #This breaks serial communciation between python and Arduino
cv2.destroyAllWindows() #This closes the window that pops up when running the code




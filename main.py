import vgamepad as vg
import time
import HandController
import cv2

def main():
    #Intialize useful objects
    hand_control = HandController.HandControl()
    gamepad = vg.VX360Gamepad()
    cap = cv2.VideoCapture(0)

    # press a button to wake the device up
    gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
    gamepad.update()
    time.sleep(0.5)
    gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
    gamepad.update()
    time.sleep(0.5)


    usedItem = False
    frameWithPalmOpenedCount = 0
    minFrameToTriggerItem = 10


    # Game loop
    while cap.isOpened():

        success, image = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            continue
        if cv2.waitKey(5) & 0xFF == 27:
            break

        #Update the current hand_control analysis
        hand_control.update(image)

        # Get speed percentage
        speed_percentage = min(max(hand_control.get_distance_between_hands() / (image.shape[1] - 100), 0), 1)

        #Accelerate or not
        if speed_percentage > 0.1 :
            gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)

        else :
            gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)


        #Use an object

        if hand_control.is_left_palm_open() :
            frameWithPalmOpenedCount += 1

            if frameWithPalmOpenedCount > minFrameToTriggerItem and usedItem == False :
                gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_Y)
                usedItem = True

        else :
            usedItem =  False
            frameWithPalmOpenedCount = 0
            gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_Y)

        #Turn

        #Get angle hands
        angle_max = 45
        angle = max(min(hand_control.get_angle_between_hands(),angle_max),-45)
        turn_percentage = angle/angle_max

        gamepad.left_joystick_float(x_value_float=turn_percentage, y_value_float=0)

        #Update joystick with inputs
        gamepad.update()

        #Display webcam
        cv2.imshow('MediaPipe Hands', hand_control.show_image_debug())

        #Sleep between analysis (if necessary)
        #time.sleep(0.05)
    cap.release()


if __name__ == '__main__':
    main()



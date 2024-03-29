import mediapipe as mp
import cv2
from math import sqrt, acos, degrees

class HandControl :

    def __init__(self):
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        self.mp_hands = mp.solutions.hands
        self.image = None
        self.image_dimensions = 0
        self.hands_landmarks_list =  []
        self.direction = None
        self.hands_pos_average = []

        self.frames_r_palm_opened = 0
        self.frames_r_palm_closed = 0
        self.is_r_palm_closed = 1

        self.frames_l_palm_opened = 0
        self.frames_l_palm_closed = 0
        self.is_l_palm_closed = 1

        self.min_frame_to_switch_state = 5

    def update(self, image) :
        self.__set_image(image)
        self.__set_landmarks_pos()
        self.__set_average_hand_coordinate()
        self.__set_good_hand_order()
        self.__switch_palms_states()

    def get_distance_between_hands(self):
        if len(self.hands_pos_average) >= 2 :
            pos1 = self.hands_pos_average[0]
            pos2 = self.hands_pos_average[1]
            sqr_dist = ( pos2[0] - pos1[0] )**2 + ( pos2[1] - pos1[1] )**2
            return sqrt(sqr_dist)
        else :
            return 0

    def get_angle_between_hands(self):
        if len(self.hands_pos_average) >= 2 :
            pos1 = self.hands_pos_average[0]
            pos2 = self.hands_pos_average[1]
            vec_hands = (pos2[0] - pos1[0] , pos2[1] - pos1[1])
            vec_comp = (0,1)
            magn_vec_hands = sqrt(vec_hands[0]**2 + vec_hands[1]**2)
            magn_vec_comp = sqrt(vec_comp[0]**2 + vec_comp[1]**2 )
            angle = acos( (vec_comp[0]*vec_hands[0] + vec_comp[1]*vec_hands[1]) / (magn_vec_comp * magn_vec_hands) )
            angle = degrees(angle)
            return angle - 90
        else :
            return 0

    def __switch_palms_states(self):
        # Left palm
        if self.is_left_palm_open() :
            self.frames_l_palm_opened += 1
            self.frames_l_palm_closed = 0
        else :
            self.frames_l_palm_closed += 1
            self.frames_l_palm_opened = 0

        if self.frames_l_palm_opened > self.min_frame_to_switch_state or self.frames_l_palm_closed > self.min_frame_to_switch_state :
            #Switch state of left palm
            if self.frames_l_palm_opened > self.frames_l_palm_closed :
                # It needs to switch to open
                self.is_l_palm_closed = 0
            else :
                self.is_l_palm_closed = 1

            self.frames_l_palm_opened = 0
            self.frames_l_palm_closed = 0

        # Right palm
        if self.is_right_palm_open():
            self.frames_r_palm_opened += 1
            self.frames_r_palm_closed = 0
        else:
            self.frames_r_palm_closed += 1
            self.frames_r_palm_opened = 0

        if self.frames_r_palm_opened > self.min_frame_to_switch_state or self.frames_r_palm_closed > self.min_frame_to_switch_state:
            # Switch state of right palm
            if self.frames_r_palm_opened > self.frames_r_palm_closed:
                # It needs to switch to open
                self.is_r_palm_closed = 0
            else:
                self.is_r_palm_closed = 1

            self.frames_r_palm_opened = 0
            self.frames_r_palm_closed = 0




    def is_left_palm_open(self):
        if len(self.hands_landmarks_list) >= 2 :
            return self.__is_palm_open(self.hands_landmarks_list[1])
        else :
            return False

    def is_right_palm_open(self):
        if len(self.hands_landmarks_list) >= 2:
            return self.__is_palm_open(self.hands_landmarks_list[0])
        else :
            return False

    def show_image_debug(self):

        img_debug = self.image

        if len(self.hands_pos_average) >= 2:

            # Draw debug point to average hand landmarks position (hopefully the hands)
            cv2.circle(img_debug, self.hands_pos_average[0], 10, (0, 0, 255), -1)
            cv2.circle(img_debug, self.hands_pos_average[1], 10, (255, 0, 0), -1)

            # Draw debug line between the hands
            cv2.line(img_debug, self.hands_pos_average[0], self.hands_pos_average[1], (0, 255, 0), 2)

            # Draw circle to simulate steering wheel
            cv2.circle(img_debug, (int((self.hands_pos_average[0][0] + self.hands_pos_average[1][0]) / 2),
                                   int((self.hands_pos_average[0][1] + self.hands_pos_average[1][1]) / 2)),
                       int(self.get_distance_between_hands() / 2), (0, 255, 0), 2)

        img_debug = cv2.flip(img_debug, 1)
        cv2.putText(img_debug, "Speed : " + str(round(self.get_distance_between_hands(),2)), (0, 500-30), cv2.FONT_HERSHEY_SIMPLEX,
                    1, (0, 255, 0), 1, 1)
        cv2.putText(img_debug, "Angle : " + str(round(self.get_angle_between_hands(),2)), (0, 500-60), cv2.FONT_HERSHEY_SIMPLEX, 1,
                    (0, 255, 0), 1, 1)
        cv2.putText(img_debug, "RPalm ? : " + str(round(self.is_r_palm_closed ,2)) + " LPalm ? : " + str(round(self.is_l_palm_closed,2)) , (0, 500-90), cv2.FONT_HERSHEY_SIMPLEX, 1,
                    (0, 255, 0), 1, 1)
        return img_debug

    def __set_landmarks_pos(self):
        with self.mp_hands.Hands(static_image_mode=True,max_num_hands=2,min_detection_confidence=0.5) as hands :
            self.image.flags.writeable = False
            self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
            results = hands.process(self.image)
            self.image.flags.writeable = True
            self.image = cv2.cvtColor(self.image, cv2.COLOR_RGB2BGR)

            self.hands_landmarks_list = []

            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    self.hands_landmarks_list.append(hand_landmarks)

    def __set_image(self, image):
        self.image = image
        self.image_dimensions = image.shape

    def __set_average_hand_coordinate(self):
        self.hands_pos_average = []
        for hand_landmark in self.hands_landmarks_list :
            self.hands_pos_average.append(self.__get_average_hand_coordinate(hand_landmark))


    def __get_average_hand_coordinate(self, hand_landmarks):
        x , y = 0 , 0
        count = 0
        for landmark in hand_landmarks.landmark :
            x += landmark.x
            y += landmark.y
            count+=1
        final_x = int(x/count * self.image_dimensions[1])
        final_y = int(y/count * self.image_dimensions[0])
        return final_x, final_y

    def __set_good_hand_order(self):
        if len(self.hands_pos_average) >= 2 :
            if (self.hands_pos_average[0][0] > self.hands_pos_average[1][0]) :
                #Swap hand pos in list
                swap_pos = self.hands_pos_average[0]
                self.hands_pos_average[0] = self.hands_pos_average[1]
                self.hands_pos_average[1] = swap_pos
                #Swap hand landmarks in list
                swap_landmarks = self.hands_landmarks_list[0]
                self.hands_landmarks_list[0] = self.hands_landmarks_list[1]
                self.hands_landmarks_list[1] = swap_landmarks


    def __is_palm_open(self, hand_landmarks):
        x , y = hand_landmarks.landmark[0].x , hand_landmarks.landmark[0].y
        gap_between_landmarks = 0
        for landmark in hand_landmarks.landmark :
            gap_between_landmarks += sqrt( (x - landmark.x)**2 + (y - landmark.y)**2)
        max_space = sqrt((hand_landmarks.landmark[0].x - hand_landmarks.landmark[-1].x)**2
                         + (hand_landmarks.landmark[0].y  - hand_landmarks.landmark[-1].y)**2)
        ratio = gap_between_landmarks/max_space

        if ratio < 17 and ratio > 0 :
            return True
        else :
            return False

